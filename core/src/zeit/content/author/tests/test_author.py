# -*- coding: utf-8 -*-
from unittest import mock
from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import ICommonMetadata
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import ObjectModifiedEvent, ObjectCreatedEvent
import requests_mock
import six.moves.urllib.parse
import zeit.cms.interfaces
import zeit.content.author.author
import zeit.content.author.testing
import zeit.find.interfaces
import zope.event


NONZERO = 3


class AuthorTest(zeit.content.author.testing.FunctionalTestCase):

    def test_author_exists(self):
        Author = zeit.content.author.author.Author
        elastic = zope.component.getUtility(zeit.find.interfaces.ICMSSearch)
        with mock.patch.object(elastic, 'search') as search:
            search.return_value = zeit.cms.interfaces.Result([])
            self.assertFalse(Author.exists('William', 'Shakespeare'))
            search.assert_called_with({'query': {'bool': {'filter': [
                {'term': {'doc_type': 'author'}},
                {'term': {'payload.xml.firstname': 'William'}},
                {'term': {'payload.xml.lastname': 'Shakespeare'}}
            ]}}})

            search.return_value.hits = NONZERO
            self.assertTrue(Author.exists('William', 'Shakespeare'))


class FreetextCopyTest(zeit.content.author.testing.FunctionalTestCase):

    def setUp(self):
        super(FreetextCopyTest, self).setUp()
        author = zeit.content.author.author.Author()
        author.firstname = 'William'
        author.lastname = 'Shakespeare'
        self.repository['author'] = author

    def test_authorships_should_be_copied_to_freetext_on_change(self):
        with checked_out(self.repository['testcontent']) as co:
            co.authorships = [co.authorships.create(self.repository['author'])]
            zope.event.notify(ObjectModifiedEvent(
                co, Attributes(ICommonMetadata, 'authorships')))
            self.assertEqual(('William Shakespeare',), co.authors)

    def test_authorships_should_not_be_copied_for_other_field_change(
            self):
        with checked_out(self.repository['testcontent']) as co:
            zope.event.notify(ObjectModifiedEvent(
                co, Attributes(ICommonMetadata, 'title')))
            self.assertEqual(('',), co.authors)

    def test_authorships_should_clear_authors_when_empty(self):
        with checked_out(self.repository['testcontent']) as co:
            co.authorships = ()
            zope.event.notify(ObjectModifiedEvent(
                co, Attributes(ICommonMetadata, 'authorships')))
            self.assertEqual((), co.authors)

    def test_authorships_should_be_copied_to_freetext_on_create(self):
        content = ExampleContentType()
        content.authorships = [
            content.authorships.create(self.repository['author'])]
        zope.event.notify(ObjectCreatedEvent(content))
        self.repository['foo'] = content
        self.assertEqual(
            ('William Shakespeare',), self.repository['foo'].authors)

    def test_authorships_should_not_be_copied_on_copy(self):
        with checked_out(self.repository['testcontent']) as co:
            co.authorships = [co.authorships.create(self.repository['author'])]
        zope.copypastemove.interfaces.IObjectCopier(
            self.repository['testcontent']).copyTo(self.repository['online'])
        self.assertEqual(
            ('',), self.repository['online']['testcontent'].authors)


class OthersTest(zeit.content.author.testing.FunctionalTestCase):

    def test_provides_dict_access_to_xml_nodes(self):
        author = zeit.content.author.author.Author()
        author.is_cook = True
        self.assertTrue(author.is_cook)
        self.assertEllipsis(
            '...<is_cook>true</is_cook>...',
            zeit.cms.testing.xmltotext(author.xml))

        author.is_cook = False
        self.assertFalse(author.is_cook)
        self.assertEllipsis(
            '...<is_cook>false</is_cook>...',
            zeit.cms.testing.xmltotext(author.xml))

        self.assertTrue(author.is_author)
        author.is_author = True
        self.assertEllipsis(
            '...<is_author>true</is_author>...',
            zeit.cms.testing.xmltotext(author.xml))

        author.is_author = False
        self.assertFalse(author.is_author)
        self.assertEllipsis(
            '...<is_author>false</is_author>...',
            zeit.cms.testing.xmltotext(author.xml))

        author.website = 'www.testeroni.com'
        self.assertEqual('www.testeroni.com', author.website)
        self.assertEllipsis(
            '...<website>www.testeroni.com</website>...',
            zeit.cms.testing.xmltotext(author.xml))

        author.website = ''
        self.assertEqual('', author.website)
        self.assertEllipsis(
            '...<website></website>...',
            zeit.cms.testing.xmltotext(author.xml))


class BiographyQuestionsTest(zeit.content.author.testing.FunctionalTestCase):

    def test_provides_dict_access_to_xml_nodes(self):
        author = zeit.content.author.author.Author()
        author.bio_questions['drive'] = 'answer'
        self.assertEqual('answer', author.bio_questions['drive'].answer)
        self.assertEllipsis(
            '...<question id="drive">answer</question>...',
            zeit.cms.testing.xmltotext(author.xml))

    def test_provides_attribute_access_for_formlib(self):
        author = zeit.content.author.author.Author()
        author.bio_questions.drive = 'answer'
        self.assertEqual('answer', author.bio_questions.drive)

    def test_uses_separate_xml_nodes_for_different_questions(self):
        author = zeit.content.author.author.Author()
        author.bio_questions['drive'] = 'answer1'
        author.bio_questions['hobby'] = 'answer2'
        author.bio_questions['drive'] = 'answer1'
        self.assertEqual('answer1', author.bio_questions['drive'].answer)
        self.assertEqual(
            1, zeit.cms.testing.xmltotext(author.xml).count('answer1'))

    def test_setting_empty_value_removes_node(self):
        author = zeit.content.author.author.Author()
        author.bio_questions['drive'] = 'answer1'
        author.bio_questions['drive'] = None
        self.assertFalse(author.xml.xpath('//question'))

    def test_uses_titles_from_source(self):
        author = zeit.content.author.author.Author()
        self.assertEqual(
            'Das treibt mich an', author.bio_questions['drive'].title)


class SSOIdConnectTest(zeit.content.author.testing.FunctionalTestCase):

    def setUp(self):
        super(SSOIdConnectTest, self).setUp()
        self.config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.author')
        self.author = zeit.content.author.author.Author()
        self.author.email = 'peter.schmidt@zeit.de'
        self.author.sso_connect = True

    def acs(self, email, **json):
        base = self.config['sso-api-url']
        url = '{}/users/{}'.format(base, six.moves.urllib.parse.quote(
            email.encode('utf8')))
        m = requests_mock.Mocker()
        m.get(url, status_code=200, json=json)
        return m

    def test_ssoid_is_set_based_on_email(self):
        with self.acs(self.author.email, id=12345):
            self.repository['author'] = self.author
        self.assertEqual(12345, self.author.ssoid)

    def test_ssoid_is_not_set_when_sso_connect_is_disabled(self):
        with self.acs(self.author.email, id=12345):
            self.author.sso_connect = False
            self.repository['author'] = self.author
        self.assertIsNone(self.author.ssoid)

    def test_ssoid_is_updated_on_changing_email(self):
        with self.acs(self.author.email, id=12345):
            self.repository['author'] = self.author
        self.assertEqual(12345, self.author.ssoid)
        with self.acs('hans.müller@zeit.de', id=67890):
            with checked_out(self.repository['author']) as co:
                co.email = 'hans.müller@zeit.de'
        self.assertEqual(67890, self.repository['author'].ssoid)

    def test_ssoid_is_deleted_on_disable_sso_connect(self):
        with self.acs(self.author.email, id=12345):
            self.repository['author'] = self.author
            with checked_out(self.repository['author']) as co:
                co.sso_connect = False
        self.assertIsNone(self.repository['author'].ssoid)

    def test_ssoid_is_deleted_on_delete_email(self):
        with self.acs(self.author.email, id=12345):
            self.repository['author'] = self.author
            with checked_out(self.repository['author']) as co:
                co.email = None
        self.assertIsNone(self.repository['author'].ssoid)

    def test_ssoid_is_updated_on_checked_out_item(self):
        with self.acs(self.author.email, id=12345):
            self.repository['author'] = self.author
        self.assertEqual(12345, self.author.ssoid)

        with self.acs('hans.müller@zeit.de', id=67890):
            with checked_out(self.repository['author']) as co:
                co.email = 'hans.müller@zeit.de'
                zope.event.notify(ObjectModifiedEvent(
                    co, Attributes(ICommonMetadata, 'email')))
                self.assertEqual(67890, co.ssoid)
                self.assertEqual(12345, self.repository['author'].ssoid)
