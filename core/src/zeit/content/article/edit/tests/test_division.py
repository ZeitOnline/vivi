# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.content.article.testing


class DivisionTest(unittest.TestCase):

    def test_teaser_attribute_should_be_added_to_xml(self):
        from zeit.content.article.edit.division import Division
        import lxml.objectify
        div = Division(None, lxml.objectify.E.division())
        teaser = u'My div teaser'
        div.teaser = teaser
        self.assertEqual(teaser, div.teaser)
        self.assertEqual(teaser, div.xml.get('teaser'))


class TestFactory(zeit.content.article.testing.FunctionalTestCase):

    def test_factory_should_create_div_node_with_type(self):
        import zeit.content.article.article
        import zeit.content.article.edit.interfaces
        import zeit.edit.interfaces
        import zope.component
        article = zeit.content.article.article.Article()
        body = zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)
        factory = zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory, 'division')
        self.assertEqual('Division', factory.title)
        div = factory()
        self.assertTrue(
            zeit.content.article.edit.interfaces.IDivision.providedBy(div))
        self.assertEqual('division', div.xml.tag)
        self.assertEqual('page', div.xml.get('type'))
