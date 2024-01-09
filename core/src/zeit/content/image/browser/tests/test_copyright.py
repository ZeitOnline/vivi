# -*- coding: utf-8 -*-
import zeit.content.image.testing

from .test_imagegroup import ImageGroupHelperMixin


class TestCopyrights(zeit.content.image.testing.BrowserTestCase, ImageGroupHelperMixin):
    def setUp(self):
        super().setUp()
        self.add_imagegroup()
        self.set_title('New Hampshire')
        self.upload_primary_image('new-hampshire-artikel.jpg')
        self.save_imagegroup()

    def bulk_change(self):
        b = self.browser
        b.open('http://localhost/++skin++cms/repository/imagegroup/' '@@set-image-copyright')
        b.getControl(name='form.copyright.combination_00').value = 'gocept'
        b.getControl(name='form.copyright.combination_01').displayValue = ['dpa']
        b.getControl(name='form.copyright.combination_03').value = 'http://www.gocept.com/'
        b.getControl('Set copyright').click()

    def test_image_group_has_bulk_copyright_link(self):
        b = self.browser
        b.open('http://localhost/++skin++cms/repository/imagegroup')
        link = b.getLink('Bulk change image copyright')
        self.assertEqual('Bulk change image copyright', link.text)
        self.assertEqual(
            "javascript:zeit.cms.lightbox_form('http://localhost/"
            "++skin++cms/repository/imagegroup/@@set-image-copyright')",
            link.url,
        )

    def test_image_group_bulk_copyright_change_shows_message(self):
        self.bulk_change()
        b = self.browser
        b.open('http://localhost/++skin++cms/repository/' 'imagegroup/@@view.html')
        self.assertIn('Copyright changed for: new-hampshire-artikel.jpg', b.contents)

    def test_image_group_bulk_copyright_are_set(self):
        self.bulk_change()
        image = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/imagegroup/new-hampshire-artikel.jpg'
        )
        metadata = zeit.content.image.interfaces.IImageMetadata(image)
        self.assertEqual(
            ('gocept', 'dpa', None, 'http://www.gocept.com/', False), metadata.copyright
        )
