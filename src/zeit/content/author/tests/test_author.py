from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import ICommonMetadata
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import ObjectModifiedEvent, ObjectCreatedEvent
import lxml.etree
import mock
import pysolr
import unittest
import zeit.cms.testing
import zeit.content.author.author
import zeit.content.author.testing
import zope.event


NONZERO = 3


class AuthorTest(unittest.TestCase):

    def test_author_exists(self):
        author = zeit.content.author.author.Author()
        author.firstname = u'William'
        author.lastname = u'Shakespeare'
        with mock.patch('zeit.find.search.query', lambda **kw: kw):
            with mock.patch('zeit.find.search.search') as search:
                search.return_value = pysolr.Results(None, hits=0)
                self.assertFalse(author.exists)
                search.assert_called_with(dict(
                    fulltext=u'William Shakespeare', types=('author',)))

                search.return_value = pysolr.Results(None, hits=NONZERO)
                self.assertTrue(author.exists)
                search.assert_called_with(dict(
                    fulltext=u'William Shakespeare', types=('author',)))


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
