import lxml.etree
import mock
import pysolr
import unittest
import zeit.cms.testing
import zeit.content.author.author
import zeit.content.author.testing


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


class ModifiedHandlerTest(unittest.TestCase):

    def test_authorships_should_be_copied_to_freetext(self):
        from zope.lifecycleevent import ObjectModifiedEvent, Attributes
        from zeit.cms.content.interfaces import ICommonMetadata
        from zeit.content.author.author import update_author_freetext
        content = mock.Mock()
        author1, author2 = mock.Mock(), mock.Mock()
        author1.target.display_name = mock.sentinel.author1
        author2.target.display_name = mock.sentinel.author2
        content.authorships = (author1, author2)
        event = ObjectModifiedEvent(
            content, Attributes(ICommonMetadata, 'authorships'))
        update_author_freetext(content, event)
        self.assertEqual([mock.sentinel.author1, mock.sentinel.author2],
                         content.authors)

    def test_authorships_should_not_be_copied_for_other_field_change(
            self):
        from zope.lifecycleevent import ObjectModifiedEvent, Attributes
        from zeit.cms.content.interfaces import ICommonMetadata
        from zeit.content.author.author import update_author_freetext
        content = mock.Mock()
        content.authors = mock.sentinel.unchanged
        author1, author2 = mock.Mock(), mock.Mock()
        content.authorships = (author1, author2)
        event = ObjectModifiedEvent(
            content, Attributes(ICommonMetadata, 'some-field'))
        update_author_freetext(content, event)
        self.assertEqual(mock.sentinel.unchanged, content.authors)

    def test_authorships_should_clear_authors_when_empty(self):
        from zope.lifecycleevent import ObjectModifiedEvent, Attributes
        from zeit.cms.content.interfaces import ICommonMetadata
        from zeit.content.author.author import update_author_freetext
        content = mock.Mock()
        content.authors = mock.sentinel.unchanged
        content.authorships = ()
        event = ObjectModifiedEvent(
            content, Attributes(ICommonMetadata, 'authorships'))
        update_author_freetext(content, event)
        self.assertEqual([], content.authors)

    def test_authorships_should_be_copied_to_freetext_for_subclasses(self):
        from zope.lifecycleevent import ObjectModifiedEvent, Attributes
        from zeit.cms.content.interfaces import ICommonMetadata
        from zeit.content.author.author import update_author_freetext

        class IArticle(ICommonMetadata):
            pass

        content = mock.Mock()
        author1, author2 = mock.Mock(), mock.Mock()
        author1.target.display_name = mock.sentinel.author1
        author2.target.display_name = mock.sentinel.author2
        content.authorships = (author1, author2)
        event = ObjectModifiedEvent(
            content, Attributes(IArticle, 'authorships'))
        update_author_freetext(content, event)
        self.assertEqual([mock.sentinel.author1, mock.sentinel.author2],
                         content.authors)


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
