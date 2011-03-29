# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import lxml.objectify
import unittest
import zeit.content.article.testing


class ParagraphTest(unittest.TestCase):

    def get_paragraph(self, p=''):
        from zeit.content.article.edit.paragraph import Paragraph
        body = lxml.objectify.E.body(lxml.objectify.XML('<p>%s</p>' % p))
        return Paragraph(None, body.p)

    def test_setting_text_inserts_xml(self):
        p = self.get_paragraph()
        self.assertEquals(u'', p.text)
        text = u'The quick brown fox jumps over the lazy dog.'
        p.text = text
        self.assertEqual(text, p.text)
        text = u'The quick brown <em>fox</em> jumps over the lazy dog.'
        p.text = text
        self.assertEqual(text, p.text)

    def test_node_tails_should_be_include_in_text(self):
        p = self.get_paragraph('Im <strong>Tal</strong> der Buchstaben')
        self.assertEqual(u'Im <strong>Tal</strong> der Buchstaben', p.text)

    def test_setting_invalid_xml_is_somehow_converted_to_valid_xml(self):
        p = self.get_paragraph()
        p.text = u'<em>4 > 3'
        self.assertEqual('<em>4 &gt; 3</em>', p.text)

    def test_setting_text_should_keep_attributes(self):
        p = self.get_paragraph()
        p.xml.set('myattr', 'avalue')
        p.text = 'Mary had a little lamb.'
        self.assertEqual('avalue', p.xml.get('myattr'))

    def test_setting_unicode_should_work(self):
        p = self.get_paragraph()
        p.text = u'F\xfc!'
        self.assertEqual(u'F\xfc!', p.text)
        self.assertTrue(isinstance(p.text, unicode))

    def test_text_should_be_unicode(self):
        p = self.get_paragraph()
        p.text = 'Dadudeldum'
        self.assertTrue(isinstance(p.text, unicode))

    def test_setting_html_should_create_proper_xml(self):
        p = self.get_paragraph()
        p.text = u'I am <strong>strong</strong><br>I am the best.'
        self.assertEqual(u'I am <strong>strong</strong><br/>I am the best.',
                         p.text)

    def test_xml_part_of_larger_tree_should_be_updated_in_place(self):
        from zeit.content.article.edit.paragraph import Paragraph
        body = lxml.objectify.E.body(lxml.objectify.XML('<p>bar</p>'))
        p = Paragraph(None, body.p)
        p.text = 'foo'
        self.assertTrue(isinstance(p.xml, lxml.objectify.ObjectifiedElement),
                        type(p.xml))

    def test_setting_html_with_block_elements_should_keep_p_as_xml_tag(self):
        p = self.get_paragraph()
        p.text = u'<h3>I am </h3><p>I am the best.</p>'
        self.assertEqual(p.type, p.xml.tag)

    def compare(self, input, expected):
        p = self.get_paragraph()
        p.text = input
        self.assertEqual(expected, p.text)

    def test_simple_text_should_be_escaped_correctly(self):
        self.compare(u'a > b', 'a &gt; b')

    def test_u_should_be_allowed(self):
        self.compare(u'I am <u>underlined</u>.', 'I am <u>underlined</u>.')

    def test_br_should_be_allowed(self):
        self.compare(u'I am <br/>here and<br/>here.',
                     'I am <br/>here and<br/>here.')

    def test_unknown_elements_should_be_removed(self):
        self.compare(u'A <sub>subtext</sub> is filtered',
                     u'A subtext is filtered')


class UnorderedListTest(ParagraphTest):

    def get_paragraph(self, p=''):
        from zeit.content.article.edit.paragraph import UnorderedList
        import lxml.objectify
        body = lxml.objectify.E.body(lxml.objectify.XML('<ul>%s</ul>' % p))
        return UnorderedList(None, body.ul)

    def compare(self, input, expected):
        input = u'<li>%s</li>' % input
        expected = u'<li>%s</li>' % expected
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
        import lxml.objectify
        body = lxml.objectify.E.body(lxml.objectify.XML('<ol>%s</ol>' % p))
        return OrderedList(None, body.ol)


class IntertitleTest(ParagraphTest):

    def get_paragraph(self, p=''):
        from zeit.content.article.edit.paragraph import Intertitle
        import lxml.objectify
        body = lxml.objectify.E.body(lxml.objectify.XML(
            '<intertitle>%s</intertitle>' % p))
        return Intertitle(None, body.intertitle)


class TestFactories(zeit.content.article.testing.FunctionalTestCase):

    def assert_factory(self, name):
        import zeit.content.article.article
        import zeit.content.article.edit.interfaces
        import zeit.edit.interfaces
        import zope.component
        article = zeit.content.article.article.Article()
        body = zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)
        factory = zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory, name)
        self.assertEqual('<%s>' % name, factory.title)
        block = factory()
        self.assertTrue(
            zeit.content.article.edit.interfaces.IParagraph.providedBy(block))
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
