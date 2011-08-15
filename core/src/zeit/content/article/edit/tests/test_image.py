# coding: utf8
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
        image.references = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/2006/DSC00109_2.JPG')
        self.assertEqual(
            'http://xml.zeit.de/2006/DSC00109_2.JPG',
            image.xml.get('src'))
        self.assertEqual(
            'http://xml.zeit.de/2006/DSC00109_2.JPG',
            image.references.uniqueId)
        self.assertEqual(u'myname', image.__name__)
        self.assertEqual(u'small', image.layout)

    def test_image_nodes_inside_p_are_migrated_on_checkout(self):
        from zeit.connector.resource import Resource
        import StringIO
        import zeit.cms.checkout.interfaces
        import zeit.cms.interfaces
        import zeit.connector.interfaces
        import zope.component
        article_xml = """
        <article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
            <head/>
            <body>
              <division type="page">
                <p>A leading para</p>
                <p><image src="myniceimage" /></p>
              </division>
            </body>
        </article>"""
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        connector.add(Resource(
            'http://xml.zeit.de/article', 'article', 'article',
            StringIO.StringIO(article_xml)))
        article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/article')
        co = zeit.cms.checkout.interfaces.ICheckoutManager(article).checkout()
        self.assertEqual(
            ['p', 'image'],
            [el.tag for el in co.xml.body.division.iterchildren()])

    def _skip_test_image_nodes_should_keep_reference_with_strange_chars(self):
        # Broken due to error in zeit.wysiwyg. I'm not going to fix this (now)
        # becuase zeit.wysiwyg shouldn't be used for article (#8194) and
        # filenames with non us-asscii charachters are almost never used.
        from zeit.connector.resource import Resource
        import StringIO
        import zeit.cms.checkout.helper
        import zeit.cms.interfaces
        import zeit.connector.interfaces
        import zope.component
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        connector.move(u'http://xml.zeit.de/2006/DSC00109_2.JPG',
                       u'http://xml.zeit.de/2006/ÄÖÜ.JPG')
        article_xml = u"""
        <article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
            <head/>
            <body>
              <division type="page">
                <p>A leading para</p>
                <image src="http://xml.zeit.de/2006/ÄÖÜ.JPG" />
              </division>
            </body>
        </article>"""
        connector.add(Resource(
            'http://xml.zeit.de/article', 'article', 'article',
            StringIO.StringIO(article_xml)))
        article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/article')
        with zeit.cms.checkout.helper.checked_out(article) as co:
            self.assertEqual(
                u'http://xml.zeit.de/2006/ÄÖÜ.JPG',
                co.xml.body.division.image.get('src'))
        article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/article')
        self.assertEqual(
            u'http://xml.zeit.de/2006/ÄÖÜ.JPG',
            article.xml.body.division.image.get('src'))


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
