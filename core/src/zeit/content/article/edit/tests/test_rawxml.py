# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt


import unittest2
import zeit.content.article.testing


class RawXMLTest(unittest2.TestCase):

    def test_root_tag_must_be_raw(self):
        from zeit.content.article.edit.interfaces import IRawXML
        import lxml.objectify
        field = IRawXML['xml']
        self.assertRaisesRegexp(
            'The root element must be <raw>',
            lambda: field.validate(lxml.objectify.E.foo()))
        field.validate(lxml.objectify.E.raw())


class TestFactory(zeit.content.article.testing.FunctionalTestCase):

    def test_factory_should_create_raw_node(self):
        import zeit.content.article.article
        import zeit.content.article.edit.interfaces
        import zeit.edit.interfaces
        import zope.component
        article = zeit.content.article.article.Article()
        body = zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)
        factory = zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory, 'raw')
        self.assertEqual('Raw XML', factory.title)
        div = factory()
        self.assertTrue(
            zeit.content.article.edit.interfaces.IRawXML.providedBy(div))
        self.assertEqual('raw', div.xml.tag)
