# coding: utf8
# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import contextlib
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

    def get_image_article(self, content):
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
                {0}
              </division>
            </body>
        </article>""".format(content)
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        connector.add(Resource(
            'http://xml.zeit.de/article', 'article', 'article',
            StringIO.StringIO(article_xml)))
        article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/article')
        return zeit.cms.checkout.interfaces.ICheckoutManager(
            article).checkout()

    def test_image_nodes_inside_p_are_migrated_on_checkout(self):
        article = self.get_image_article("""
                <p>A leading para</p>
                <p>Blarf<image src="myniceimage" /></p>
                                         """)
        self.assertEqual(
            ['p', 'image', 'p'],
            [el.tag for el in article.xml.body.division.iterchildren()])

    def test_empty_p_nodes_should_be_removed_on_image_migrate(self):
        article = self.get_image_article("""
                <p>A leading para</p>
                <p><image src="myniceimage" /></p>
                               """)
        self.assertEqual(
            ['p', 'image'],
            [el.tag for el in article.xml.body.division.iterchildren()])

    def test_image_tail_should_be_preserved_on_migrate(self):
        article = self.get_image_article("""
                <p>A leading para</p>
                <p><image src="myniceimage" /> a tail</p>
                               """)
        self.assertEqual(
            ['p', 'image', 'p'],
            [el.tag for el in article.xml.body.division.iterchildren()])
        self.assertEqual(
            ' a tail', article.xml.body.division.p[1].text)

    def test_image_should_be_moved_up_to_division_even_when_deeper_nested(
        self):
        article = self.get_image_article("""
                <p>A leading para</p>
                <p><strong> blah <image src="myniceimage" /></strong></p>
                               """)
        self.assertEqual(
            ['p', 'image', 'p'],
            [el.tag for el in article.xml.body.division.iterchildren()])

    def test_image_nodes_should_keep_reference_with_strange_chars_on_checkout(
        self):
        import zeit.connector.interfaces
        import zope.component
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        connector.move(u'http://xml.zeit.de/2006/DSC00109_2.JPG',
                       u'http://xml.zeit.de/2006/ÄÖÜ.JPG')
        article = self.get_image_article("""
                <p>A leading para</p>
                <image src="http://xml.zeit.de/2006/ÄÖÜ.JPG" />""")
        self.assertEqual(
            u'http://xml.zeit.de/2006/ÄÖÜ.JPG',
            article.xml.body.division.image.get('src'))

    def test_image_nodes_should_keep_reference_with_strange_chars_on_checkin(
        self):
        from zeit.content.article.interfaces import IArticle
        import zeit.cms.browser.form
        import zeit.cms.checkout.interfaces
        import zeit.cms.interfaces
        import zeit.connector.interfaces
        import zope.component
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        connector.move(u'http://xml.zeit.de/2006/DSC00109_2.JPG',
                       u'http://xml.zeit.de/2006/ÄÖÜ.JPG')
        article = self.get_image_article("""
                <p>A leading para</p>
                <image src="http://xml.zeit.de/2006/ÄÖÜ.JPG" />""")
        zeit.cms.browser.form.apply_default_values(article, IArticle)
        article.year = 2011
        article.title = u'title'
        article.ressort = u'Deutschland'
        article = zeit.cms.checkout.interfaces.ICheckinManager(
            article).checkin()
        self.assertEqual(
            u'http://xml.zeit.de/2006/ÄÖÜ.JPG',
            article.xml.body.division.image.get('src'))

    def test_image_referenced_via_IImages_is_copied_to_first_body_block(self):
        from zeit.content.article.article import Article
        from zeit.content.article.interfaces import IArticle
        from zeit.content.article.edit.interfaces import IEditableBody
        from zeit.content.image.interfaces import IImages
        import zeit.cms.browser.form
        import zeit.cms.interfaces
        import zope.lifecycleevent

        article = Article()
        zeit.cms.browser.form.apply_default_values(article, IArticle)
        article.year = 2011
        article.title = u'title'
        article.ressort = u'Deutschland'
        self.repository['article'] = article

        with zeit.cms.checkout.helper.checked_out(
            self.repository['article']) as co:
            body = IEditableBody(co)
            factory = zope.component.getAdapter(
                body, zeit.edit.interfaces.IElementFactory, 'image')
            image_block = factory()

            image_id = 'http://xml.zeit.de/2006/DSC00109_2.JPG'
            IImages(co).images = [zeit.cms.interfaces.ICMSContent(image_id)]
            zope.lifecycleevent.modified(
                co, zope.lifecycleevent.Attributes(IImages, 'images'))

            image_block = body.values()[0]
            self.assertEqual(image_block.references.uniqueId, image_id)

    def test_IImages_is_not_copied_to_body_if_first_block_has_an_image(self):
        from zeit.content.article.article import Article
        from zeit.content.article.interfaces import IArticle
        from zeit.content.article.edit.interfaces import IEditableBody
        from zeit.content.image.interfaces import IImages
        import zeit.cms.browser.form
        import zeit.cms.interfaces
        import zeit.content.image.tests
        import zope.lifecycleevent

        image_group = zeit.content.image.tests.create_image_group()
        article = Article()
        zeit.cms.browser.form.apply_default_values(article, IArticle)
        article.year = 2011
        article.title = u'title'
        article.ressort = u'Deutschland'
        self.repository['article'] = article
        with zeit.cms.checkout.helper.checked_out(
            self.repository['article']) as co:
            body = IEditableBody(co)
            factory = zope.component.getAdapter(
                body, zeit.edit.interfaces.IElementFactory, 'image')
            image_block = factory()
            image_block.references = image_group

            image_id = 'http://xml.zeit.de/2006/DSC00109_2.JPG'
            IImages(co).images = [zeit.cms.interfaces.ICMSContent(image_id)]
            zope.lifecycleevent.modified(
                co, zope.lifecycleevent.Attributes(IImages, 'images'))

            image_block = body.values()[0]
            self.assertEqual(
                image_block.references.uniqueId, image_group.uniqueId)

    @contextlib.contextmanager
    def image(self):
        from zeit.cms.interfaces import ICMSContent
        from zeit.content.article.article import Article
        from zeit.content.article.interfaces import IArticle
        import zeit.cms.browser.form
        import zeit.cms.checkout.helper
        import zeit.content.article.edit.body
        import zeit.edit.interfaces
        import zope.component
        article = Article()
        zeit.cms.browser.form.apply_default_values(article, IArticle)
        article.year = 2011
        article.title = u'title'
        article.ressort = u'Deutschland'
        self.repository['article'] = article
        with zeit.cms.checkout.helper.checked_out(
            self.repository['article']) as article:
            body = zeit.content.article.edit.body.EditableBody(
                article, article.xml.body)
            factory = zope.component.getAdapter(
                body, zeit.edit.interfaces.IElementFactory, 'image')
            image = factory()
            image.references = ICMSContent(
                'http://xml.zeit.de/2006/DSC00109_2.JPG')
            yield image

    def test_custom_caption_should_be_set_to_bu_tag(self):
        with self.image() as image:
            image.custom_caption = u'a custom caption'
        self.assertEqual(
            u'a custom caption',
            self.repository['article'].xml.body.division.image.bu)

    def test_custom_caption_should_be_kept_on_checkin(self):
        with self.image() as image:
            image.custom_caption = u'a custom caption'
        self.assertEqual(
            u'a custom caption',
            self.repository['article'].xml.body.division.image.get(
                'custom-caption'))

    def test_setting_reference_should_not_remove_custom_caption(self):
        from zeit.cms.interfaces import ICMSContent
        with self.image() as image:
            image.custom_caption = u'a custom caption'
            image.references = ICMSContent(
                'http://xml.zeit.de/2006/DSC00109_2.JPG')
        self.assertEqual(
            u'a custom caption',
            self.repository['article'].xml.body.division.image.get(
                'custom-caption'))


class TestFactory(zeit.content.article.testing.FunctionalTestCase):

    def test_factory_should_create_image_node(self):
        import zeit.content.article.article
        import zeit.content.article.edit.body
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
