import unittest

import lxml.builder
import lxml.etree

import zeit.content.article.testing


class ParagraphTest(unittest.TestCase):
    def get_paragraph(self, p=''):
        from zeit.content.article.edit.paragraph import Paragraph

        body = lxml.builder.E.body(lxml.etree.fromstring('<p>%s</p>' % p))
        return Paragraph(None, body.p)

    def test_setting_text_inserts_xml(self):
        p = self.get_paragraph()
        self.assertEqual('', p.text)
        text = 'The quick brown fox jumps over the lazy dog.'
        p.text = text
        self.assertEqual(text, p.text)
        text = 'The quick brown <em>fox</em> jumps over the lazy dog.'
        p.text = text
        self.assertEqual(text, p.text)

    def test_node_tails_should_be_include_in_text(self):
        p = self.get_paragraph('Im <strong>Tal</strong> der Buchstaben')
        self.assertEqual('Im <strong>Tal</strong> der Buchstaben', p.text)

    def test_setting_invalid_xml_is_somehow_converted_to_valid_xml(self):
        p = self.get_paragraph()
        p.text = '<em>4 > 3'
        self.assertEqual('<em>4 &gt; 3</em>', p.text)

    def test_setting_text_should_keep_attributes(self):
        p = self.get_paragraph()
        p.xml.set('myattr', 'avalue')
        p.text = 'Mary had a little lamb.'
        self.assertEqual('avalue', p.xml.get('myattr'))

    def test_setting_unicode_should_work(self):
        p = self.get_paragraph()
        p.text = 'F\xfc!'
        self.assertEqual('F\xfc!', p.text)
        self.assertTrue(isinstance(p.text, str))

    def test_text_should_be_unicode(self):
        p = self.get_paragraph()
        p.text = 'Dadudeldum'
        self.assertTrue(isinstance(p.text, str))

    def test_setting_html_should_create_proper_xml(self):
        p = self.get_paragraph()
        p.text = 'I am <strong>strong</strong><br>I am the best.'
        self.assertEqual('I am <strong>strong</strong><br/>I am the best.', p.text)

    def test_xml_part_of_larger_tree_should_be_updated_in_place(self):
        from zeit.content.article.edit.paragraph import Paragraph

        body = lxml.builder.E.body(lxml.etree.fromstring('<p>bar</p>'))
        p = Paragraph(None, body.p)
        p.text = 'foo'
        self.assertTrue(isinstance(p.xml, lxml.etree._Element), type(p.xml))

    def test_setting_html_with_block_elements_should_keep_p_as_xml_tag(self):
        p = self.get_paragraph()
        p.text = '<h3>I am </h3><p>I am the best.</p>'
        self.assertEqual(p.type, p.xml.tag)

    def compare(self, input, expected):
        p = self.get_paragraph()
        p.text = input
        self.assertEqual(expected, p.text)

    def test_simple_text_should_be_escaped_correctly(self):
        self.compare('a > b', 'a &gt; b')

    def test_u_should_be_allowed(self):
        self.compare('I am <u>underlined</u>.', 'I am <u>underlined</u>.')

    def test_br_should_be_allowed(self):
        self.compare('I am <br/>here and<br/>here.', 'I am <br/>here and<br/>here.')

    def test_unknown_elements_should_be_removed(self):
        self.compare('A <sub>subtext</sub> is filtered', 'A subtext is filtered')

    def test_leading_spaces_are_preserved(self):
        self.compare('<em> <a>foo</a> bar</em>', '<em> <a>foo</a> bar</em>')

    def test_regression_after_beautiful_soup_update(self):
        self.compare('<b>foo</b> bar baz', '<b>foo</b> bar baz')


class UnorderedListTest(ParagraphTest):
    def get_paragraph(self, p=''):
        from zeit.content.article.edit.paragraph import UnorderedList

        body = lxml.builder.E.body(lxml.etree.fromstring('<ul>%s</ul>' % p))
        return UnorderedList(None, body.ul)

    def compare(self, input, expected):
        input = '<li>%s</li>' % input
        expected = '<li>%s</li>' % expected
        p = self.get_paragraph()
        p.text = input
        self.assertEqual(expected, p.text)

    def test_li_should_be_allowed(self):
        p = self.get_paragraph()
        p.text = '<li>foo</li>'
        self.assertEqual('<li>foo</li>', p.text)


class OrderedListTest(UnorderedListTest):
    def get_paragraph(self, p=''):
        from zeit.content.article.edit.paragraph import OrderedList

        body = lxml.builder.E.body(lxml.etree.fromstring('<ol>%s</ol>' % p))
        return OrderedList(None, body.ol)


class IntertitleTest(ParagraphTest):
    def get_paragraph(self, p=''):
        from zeit.content.article.edit.paragraph import Intertitle

        body = lxml.builder.E.body(lxml.etree.fromstring('<intertitle>%s</intertitle>' % p))
        return Intertitle(None, body.intertitle)


class LegacyInitialParagraphTest(ParagraphTest):
    def get_paragraph(self, p=''):
        from zeit.content.article.edit.paragraph import LegacyInitialParagraph

        body = lxml.builder.E.body(lxml.etree.fromstring('<initial>%s</initial>' % p))
        return LegacyInitialParagraph(None, body.initial)


class TestFactories(zeit.content.article.testing.FunctionalTestCase):
    def assert_factory(self, name):
        import zope.component

        import zeit.content.article.article
        import zeit.content.article.edit.interfaces
        import zeit.edit.interfaces

        article = zeit.content.article.article.Article()
        body = zeit.content.article.edit.body.EditableBody(article, article.xml.body)
        factory = zope.component.getAdapter(body, zeit.edit.interfaces.IElementFactory, name)
        # so they don't show up in the module library
        self.assertEqual(None, factory.title)
        block = factory()
        self.assertTrue(zeit.content.article.edit.interfaces.IParagraph.providedBy(block))
        self.assertEqual(name, block.xml.tag)
        self.assertEqual('division', block.xml.getparent().tag)
        return block

    def test_p(self):
        self.assert_factory('p')

    def test_ul(self):
        self.assert_factory('ul')

    def test_ol(self):
        self.assert_factory('ol')

    def test_intertitle(self):
        self.assert_factory('intertitle')
