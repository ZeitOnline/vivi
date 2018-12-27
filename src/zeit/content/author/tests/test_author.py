# -*- coding: utf-8 -*-
from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import ICommonMetadata
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import ObjectModifiedEvent, ObjectCreatedEvent
import lxml.etree
import mock
import requests_mock
import urllib
import zeit.cms.interfaces
import zeit.cms.testing
import zeit.content.author.author
import zeit.content.author.testing
import zeit.find.interfaces
import zope.event


NONZERO = 3


class AuthorTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.author.testing.ZCML_LAYER

    def test_author_exists(self):
        author = zeit.content.author.author.Author()
        author.firstname = u'William'
        author.lastname = u'Shakespeare'
        elastic = zope.component.getUtility(zeit.find.interfaces.ICMSSearch)
        with mock.patch.object(elastic, 'search') as search:
            search.return_value = zeit.cms.interfaces.Result([])
            self.assertFalse(author.exists)
            search.assert_called_with({'query': {'bool': {'filter': [
                {'term': {'doc_type': 'author'}},
                {'term': {'payload.xml.firstname': 'William'}},
                {'term': {'payload.xml.lastname': 'Shakespeare'}}
            ]}}})

            search.return_value.hits = NONZERO
            self.assertTrue(author.exists)


class FreetextCopyTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.author.testing.ZCML_LAYER

    def setUp(self):
        super(FreetextCopyTest, self).setUp()
        author = zeit.content.author.author.Author()
        author.firstname = u'William'
        author.lastname = u'Shakespeare'
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


class BiographyQuestionsTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.author.testing.ZCML_LAYER

    def test_provides_dict_access_to_xml_nodes(self):
        author = zeit.content.author.author.Author()
        author.bio_questions['drive'] = 'answer'
        self.assertEqual('answer', author.bio_questions['drive'].answer)
        self.assertEllipsis(
            '...<question id="drive">answer</question>...',
            lxml.etree.tostring(author.xml))

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
        self.assertEqual(1, lxml.etree.tostring(author.xml).count('answer1'))

    def test_setting_empty_value_removes_node(self):
        author = zeit.content.author.author.Author()
        author.bio_questions['drive'] = 'answer1'
        author.bio_questions['drive'] = None
        self.assertFalse(author.xml.xpath('//question'))

    def test_uses_titles_from_source(self):
        author = zeit.content.author.author.Author()
        self.assertEqual(
            'Das treibt mich an', author.bio_questions['drive'].title)


class SSOIdConnectTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.author.testing.ZCML_LAYER

    def setUp(self):
        super(SSOIdConnectTest, self).setUp()
        self.config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.author')
        self.author = zeit.content.author.author.Author()
        self.author.email = u'peter.schmidt@zeit.de'
        self.author.sso_connect = True
        self.url = self.config['sso-api-url'] + '/users/' + urllib.quote(
            self.author.email.encode('utf8'))

    def test_ssoid_is_set_based_on_email(self):
        with requests_mock.Mocker() as m:
            m.get(self.url, status_code=200, json={'id': '12345'})
            self.repository['author'] = self.author
            self.assertEqual('12345', self.author.ssoid)

    def test_ssoid_is_not_set_when_sso_connect_is_disabled(self):
        with requests_mock.Mocker() as m:
            m.get(self.url, status_code=200, json={'id': '12345'})
            self.author.sso_connect = False
            self.repository['author'] = self.author
            self.assertIsNone(self.author.ssoid)

    def test_ssoid_is_updated_on_changing_email(self):
        with requests_mock.Mocker() as m:
            m.get(self.url, status_code=200, json={'id': '12345'})
            self.repository['author'] = self.author
            with checked_out(self.repository['author']) as co:
                co.email = u'hans.müller@zeit.de'
                url = self.config['sso-api-url'] + '/users/' + urllib.quote(
                    co.email.encode('utf8'))
                m.get(url, status_code=200, json={'id': '67890'})
                zope.event.notify(ObjectModifiedEvent(
                    co, Attributes(ICommonMetadata, 'email')))
                self.assertEqual('67890', co.ssoid)

    def test_ssoid_is_deleted_on_disable_sso_connect(self):
        with requests_mock.Mocker() as m:
            m.get(self.url, status_code=200, json={'id': '12345'})
            self.repository['author'] = self.author
            with checked_out(self.repository['author']) as co:
                co.sso_connect = False
                zope.event.notify(ObjectModifiedEvent(
                    co, Attributes(ICommonMetadata, 'sso_connect')))
                self.assertIsNone(co.ssoid)

    def test_ssoid_is_deleted_on_delete_email(self):
        with requests_mock.Mocker() as m:
            m.get(self.url, status_code=200, json={'id': '12345'})
            self.repository['author'] = self.author
            with checked_out(self.repository['author']) as co:
                co.email = None
                zope.event.notify(ObjectModifiedEvent(
                    co, Attributes(ICommonMetadata, 'email')))
                self.assertIsNone(co.ssoid)
