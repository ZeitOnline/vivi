import lxml.objectify

import zeit.content.article.article
import zeit.content.article.edit.body
import zeit.content.article.testing


class XMLReplaceTest(zeit.content.article.testing.FunctionalTestCase):
    def create_body(self, body):
        article = zeit.content.article.article.Article()
        article.xml.body = lxml.objectify.XML(
            '<body><division type="page">%s</division></body>' % body
        )
        return zeit.content.article.edit.body.EditableBody(article, article.xml.body)

    def replace(self, body, find, replace):
        body = self.create_body(body)
        zeit.content.article.edit.interfaces.IFindReplace(body).replace_all(find, replace)
        return body

    def test_replaces_inside_paragraphs(self):
        body = self.replace('<p>foo bar foo bar</p><p>foo</p>', 'foo', 'qux')
        self.assertEqual(['qux bar qux bar', 'qux'], [x.text for x in body.xml.division.p])

    def test_ignores_non_paragraph_blocks(self):
        body = self.replace('<image>foo</image>', 'foo', 'qux')
        self.assertEqual('foo', body.xml.division.image.text)

    def test_replaces_inside_lists(self):
        body = self.replace('<ul><li>foo bar foo</li><li>bar</li><li>foo</li></ul>', 'foo', 'qux')
        self.assertEqual(['qux bar qux', 'bar', 'qux'], [x.text for x in body.xml.division.ul.li])

    def test_returns_match_count(self):
        body = self.create_body('<p>foo bar foo bar</p><p>foo</p>')
        count = zeit.content.article.edit.interfaces.IFindReplace(body).replace_all('foo', 'qux')
        self.assertEqual(3, count)
