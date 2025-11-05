import lxml.builder
import zope.component

import zeit.content.article.article
import zeit.content.article.edit.body
import zeit.content.article.edit.interfaces
import zeit.content.article.testing
import zeit.content.image.testing
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

    def test_text_attribute_should_be_stored_in_xml(self):
        from zeit.content.article.edit.scrolly_image import ScrollyImage

        scrolly_img = ScrollyImage(None, lxml.builder.E.scrolly_image())
        text = 'This is some scrollytelling text'
        scrolly_img.text = text
        self.assertEqual(text, scrolly_img.text)
        self.assertEqual(text, scrolly_img.xml.get('text'))

    def test_text_display_attribute_should_be_stored_in_xml(self):
        from zeit.content.article.edit.scrolly_image import ScrollyImage

        scrolly_img = ScrollyImage(None, lxml.builder.E.scrolly_image())
        text_display = 'unboxed'
        scrolly_img.text_display = text_display
        self.assertEqual(text_display, scrolly_img.text_display)
        self.assertEqual(text_display, scrolly_img.xml.get('text-display'))

    def test_text_display_default_should_be_boxed(self):
        scrolly_img = self.create_scrolly_image()
        self.assertEqual('boxed', scrolly_img.text_display)

    def test_layout_desktop_attribute_should_be_stored_in_xml(self):
        from zeit.content.article.edit.scrolly_image import ScrollyImage

        scrolly_img = ScrollyImage(None, lxml.builder.E.scrolly_image())
        layout_desktop = 'contain'
        scrolly_img.layout_desktop = layout_desktop
        self.assertEqual(layout_desktop, scrolly_img.layout_desktop)
        self.assertEqual(layout_desktop, scrolly_img.xml.get('layout-desktop'))

    def test_layout_desktop_default_should_be_cover(self):
        scrolly_img = self.create_scrolly_image()
        self.assertEqual('cover', scrolly_img.layout_desktop)

    def test_layout_mobile_attribute_should_be_stored_in_xml(self):
        from zeit.content.article.edit.scrolly_image import ScrollyImage

        scrolly_img = ScrollyImage(None, lxml.builder.E.scrolly_image())
        layout_mobile = 'padded'
        scrolly_img.layout_mobile = layout_mobile
        self.assertEqual(layout_mobile, scrolly_img.layout_mobile)
        self.assertEqual(layout_mobile, scrolly_img.xml.get('layout-mobile'))

    def test_layout_mobile_default_should_be_cover(self):
        scrolly_img = self.create_scrolly_image()
        self.assertEqual('cover', scrolly_img.layout_mobile)

    def test_references_should_accept_image_group(self):
        scrolly_img = self.create_scrolly_image()
        image_ref = self.repository['2006']['DSC00109_2.JPG']
        scrolly_img.references = image_ref
        self.assertEqual(image_ref.uniqueId, scrolly_img.xml.get('href'))

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
