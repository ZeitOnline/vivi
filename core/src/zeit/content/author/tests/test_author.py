# -*- coding: utf-8 -*-
from unittest import mock
import urllib.parse

from zope.lifecycleevent import Attributes, ObjectModifiedEvent
import requests_mock
import zope.event

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import ICommonMetadata
import zeit.cms.config
import zeit.cms.interfaces
import zeit.content.author.author
import zeit.content.author.interfaces
import zeit.content.author.testing
import zeit.find.interfaces


NONZERO = 3


class AuthorTest(zeit.content.author.testing.FunctionalTestCase):
    def test_author_exists(self):
        Author = zeit.content.author.author.Author
        elastic = zope.component.getUtility(zeit.find.interfaces.ICMSSearch)
        with mock.patch.object(elastic, 'search') as search:
            search.return_value = zeit.cms.interfaces.Result([])
            self.assertFalse(Author.exists('William', 'Shakespeare'))
            search.assert_called_with(
                {
                    'query': {
                        'bool': {
                            'filter': [
                                {'term': {'doc_type': 'author'}},
                                {'term': {'payload.xml.firstname': 'William'}},
                                {'term': {'payload.xml.lastname': 'Shakespeare'}},
                            ]
                        }
                    }
                }
            )

            search.return_value.hits = NONZERO
            self.assertTrue(Author.exists('William', 'Shakespeare'))

    def test_author_id_is_not_too_big_validation(self):
        # ZO-3671
        author = zeit.content.author.author.Author()
        author.ssoid = 10044347
        errors = zope.schema.getValidationErrors(zeit.content.author.interfaces.IAuthor, author)
        ssoid_errors = [i for i in errors if i[0] == 'ssoid']
        assert not ssoid_errors, "Validation error for 'ssoid' should not exist"


class OthersTest(zeit.content.author.testing.FunctionalTestCase):
    def test_provides_dict_access_to_xml_nodes(self):
        author = zeit.content.author.author.Author()

        author.website = 'www.testeroni.com'
        self.assertEqual('www.testeroni.com', author.website)
        self.assertEllipsis(
            '...<website>www.testeroni.com</website>...', zeit.cms.testing.xmltotext(author.xml)
        )

        author.website = ''
        self.assertEqual('', author.website)
        self.assertEllipsis('...<website></website>...', zeit.cms.testing.xmltotext(author.xml))


class BiographyQuestionsTest(zeit.content.author.testing.FunctionalTestCase):
    def test_provides_dict_access_to_xml_nodes(self):
        author = zeit.content.author.author.Author()
        author.bio_questions['drive'] = 'answer'
        self.assertEqual('answer', author.bio_questions['drive'].answer)
        self.assertEllipsis(
            '...<question id="drive">answer</question>...', zeit.cms.testing.xmltotext(author.xml)
        )

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
        self.assertEqual(1, zeit.cms.testing.xmltotext(author.xml).count('answer1'))

    def test_setting_empty_value_removes_node(self):
        author = zeit.content.author.author.Author()
        author.bio_questions['drive'] = 'answer1'
        author.bio_questions['drive'] = None
        self.assertFalse(author.xml.xpath('//question'))

    def test_uses_titles_from_source(self):
        author = zeit.content.author.author.Author()
        self.assertEqual('Das treibt mich an', author.bio_questions['drive'].title)


class SSOIdConnectTest(zeit.content.author.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.author = zeit.content.author.author.Author()
        self.author.email = 'peter.schmidt@zeit.de'
        self.author.sso_connect = True

    def acs(self, email, **json):
        base = zeit.cms.config.required('zeit.content.author', 'sso-api-url')
        url = '{}/users/{}'.format(base, urllib.parse.quote(email.encode('utf8')))
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
                zope.event.notify(ObjectModifiedEvent(co, Attributes(ICommonMetadata, 'email')))
                self.assertEqual(67890, co.ssoid)
                self.assertEqual(12345, self.repository['author'].ssoid)
