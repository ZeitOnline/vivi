# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.content.article.testing


class ImageTest(zeit.content.article.testing.FunctionalTestCase):

    def test_image_can_be_set(self):
        from zeit.content.article.edit.image import Image
        import lxml.objectify
        import zeit.cms.interfaces
        tree = lxml.objectify.E.tree(
            lxml.objectify.E.image())
        image = Image(None, tree.image)
        image.__name__ = u'myname'
        image.layout = u'small'
        image.image = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/2006/DSC00109_2.JPG')
        self.assertEqual(
            'http://xml.zeit.de/2006/DSC00109_2.JPG',
            image.xml.get('src'))
        self.assertEqual(
            'http://xml.zeit.de/2006/DSC00109_2.JPG',
            image.image.uniqueId)
        self.assertEqual(u'myname', image.__name__)
        self.assertEqual(u'small', image.layout)


class TestFactory(zeit.content.article.testing.FunctionalTestCase):

    def test_factory_should_create_image_node(self):
        import zeit.content.article.article
        import zeit.content.article.edit.interfaces
        import zeit.edit.interfaces
        import zope.component
        article = zeit.content.article.article.Article()
        body = zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)
        factory = zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory, 'image')
        self.assertEqual('Image', factory.title)
        div = factory()
        self.assertTrue(
            zeit.content.article.edit.interfaces.IImage.providedBy(div))
        self.assertEqual('image', div.xml.tag)
