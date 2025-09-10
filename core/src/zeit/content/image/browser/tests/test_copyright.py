# -*- coding: utf-8 -*-
import zeit.content.image.testing


class TestCopyrights(zeit.content.image.testing.BrowserTestCase):
    def bulk_change(self):
        b = self.browser
        b.open('/repository/group/@@set-image-copyright')
        b.getControl(name='form.copyright.combination_00').value = 'gocept'
        b.getControl(name='form.copyright.combination_01').displayValue = ['dpa']
        b.getControl(name='form.copyright.combination_03').value = 'http://www.gocept.com/'
        b.getControl('Set copyright').click()

    def test_image_group_has_bulk_copyright_link(self):
        b = self.browser
        b.open('/repository/group')
        link = b.getLink('Bulk change image copyright')
        self.assertEqual('Bulk change image copyright', link.text)
        self.assertEqual(
            "javascript:zeit.cms.lightbox_form('http://localhost/"
            "++skin++vivi/repository/group/@@set-image-copyright')",
            link.url,
        )

    def test_image_group_bulk_copyright_change_shows_message(self):
        self.bulk_change()
        b = self.browser
        b.open('/repository/group/@@view.html')
        self.assertIn('Copyright changed for: master-image.jpg', b.contents)

    def test_image_group_bulk_copyright_are_set(self):
        self.bulk_change()
        image = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/group/master-image.jpg')
        metadata = zeit.content.image.interfaces.IImageMetadata(image)
        self.assertEqual(
            ('gocept', 'dpa', None, 'http://www.gocept.com/', False), metadata.copyright
        )
