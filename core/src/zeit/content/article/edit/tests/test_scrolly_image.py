import lxml.builder
import zope.component

import zeit.content.animation.animation
import zeit.content.article.article
import zeit.content.article.edit.body
import zeit.content.article.edit.interfaces
import zeit.content.article.testing
import zeit.content.image.testing
import zeit.content.video.video
import zeit.edit.interfaces


class ScrollyImageTest(zeit.content.article.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.article = zeit.content.article.article.Article()
        self.body = zeit.content.article.edit.body.EditableBody(
            self.article, self.article.xml.find('body')
        )

    def create_scrolly_image(self):
        factory = zope.component.getAdapter(
            self.body, zeit.edit.interfaces.IElementFactory, 'scrolly_image'
        )
        return factory()

    def test_factory_should_create_scrolly_image_node(self):
        scrolly_img = self.create_scrolly_image()
        self.assertTrue(zeit.content.article.edit.interfaces.IScrollyImage.providedBy(scrolly_img))
        self.assertEqual('scrolly_image', scrolly_img.xml.tag)

    def test_all_attributes_should_be_stored_in_xml(self):
        from zeit.content.article.edit.scrolly_image import ScrollyImage

        scrolly_img = ScrollyImage(None, lxml.builder.E.scrolly_image())
        text = 'This is some scrollytelling text'
        layout_desktop = 'contain'
        layout_mobile = 'contain-padded'

        scrolly_img.text = text
        scrolly_img.layout_desktop = layout_desktop
        scrolly_img.layout_mobile = layout_mobile

        self.assertEqual(text, scrolly_img.text)
        self.assertEqual(text, scrolly_img.xml.get('text'))

        self.assertEqual(layout_desktop, scrolly_img.layout_desktop)
        self.assertEqual(layout_desktop, scrolly_img.xml.get('layout-desktop'))

        self.assertEqual(layout_mobile, scrolly_img.layout_mobile)
        self.assertEqual(layout_mobile, scrolly_img.xml.get('layout-mobile'))

    def test_layout_desktop_default_should_be_cover(self):
        scrolly_img = self.create_scrolly_image()
        self.assertEqual('cover', scrolly_img.layout_desktop)

    def test_layout_mobile_default_should_be_cover(self):
        scrolly_img = self.create_scrolly_image()
        self.assertEqual('cover', scrolly_img.layout_mobile)

    def test_references_should_accept_image(self):
        from zeit.content.image.testing import create_image

        scrolly_img = self.create_scrolly_image()
        image = create_image()
        self.repository['image'] = image
        scrolly_img.references = image
        self.assertEqual(image.uniqueId, scrolly_img.xml.get('href'))

    def test_references_should_accept_image_group(self):
        from zeit.content.image.testing import create_image_group

        scrolly_img = self.create_scrolly_image()
        image_group = create_image_group()
        self.repository['imagegroup'] = image_group
        scrolly_img.references = image_group
        self.assertEqual(image_group.uniqueId, scrolly_img.xml.get('href'))

    def test_references_should_accept_animation(self):
        scrolly_img = self.create_scrolly_image()

        # create animation
        self.repository['article'] = zeit.content.article.article.Article()
        self.repository['video'] = zeit.content.video.video.Video()
        animation = zeit.content.animation.animation.Animation()
        animation.article = self.repository['article']
        animation.video = self.repository['video']
        self.repository['animation'] = animation
        scrolly_img.references = animation

        self.assertEqual(animation.uniqueId, scrolly_img.xml.get('href'))

    def test_references_should_be_retrievable(self):
        scrolly_img = self.create_scrolly_image()
        image_ref = self.repository['2006']['DSC00109_2.JPG']
        scrolly_img.references = image_ref
        self.assertEqual(image_ref, scrolly_img.references)

    def test_factory_title_should_be_scrollytelling_image(self):
        factory = zope.component.getAdapter(
            self.body, zeit.edit.interfaces.IElementFactory, 'scrolly_image'
        )
        self.assertEqual('Scrollytelling Image', factory.title)
