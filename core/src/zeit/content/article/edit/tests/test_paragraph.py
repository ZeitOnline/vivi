# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.content.article.testing


class ParagraphTest(unittest.TestCase):

    def get_paragraph(self, p='<p/>'):
        from zeit.content.article.edit.paragraph import Paragraph
        import lxml.objectify
        body = lxml.objectify.E.body(lxml.objectify.XML(p))
        return Paragraph(None, body.p)

    def test_setting_text_inserts_xml(self):
        p = self.get_paragraph()
        self.assertEquals(u'', p.text)
        text =  u'The quick brown fox jumps over the lazy dog.'
        p.text = text
        self.assertEqual(text, p.text)
        text =  u'The quick brown <em>fox</em> jumps over the lazy dog.'
        p.text = text
        self.assertEqual(text, p.text)

    def test_node_tails_should_be_include_in_text(self):
        p = self.get_paragraph('<p>Im <strong>Tal</strong> der Buchstaben</p>')
        self.assertEqual(u'Im <strong>Tal</strong> der Buchstaben', p.text)

    def test_setting_invalid_xml_raises_valueerror(self):
        p = self.get_paragraph()
        def fail():
            p.text = u'4 < 3'
        self.assertRaises(ValueError, fail)

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
        import lxml.objectify
        p = self.get_paragraph()
        p.text = u'I am <strong>strong</strong><br>I am the best.'
        self.assertEqual(u'I am <strong>strong</strong><br/>I am the best.',
                         p.text)
        self.assertTrue(isinstance(p.xml, lxml.objectify.ObjectifiedElement),
                        type(p.xml))


class TestFactory(zeit.content.article.testing.FunctionalTestCase):

    def test_factory_should_create_p_node(self):
        import zeit.content.article.article
        import zeit.content.article.edit.interfaces
        import zeit.edit.interfaces
        import zope.component
        article = zeit.content.article.article.Article()
        body = zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)
        factory = zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory, 'p')
        self.assertEqual('Paragraph', factory.title)
        p = factory()
        self.assertTrue(
            zeit.content.article.edit.interfaces.IParagraph.providedBy(p))
        self.assertEqual('p', p.xml.tag)
        self.assertEqual('division', p.xml.getparent().tag)
