import PIL
import transaction

import zeit.content.gallery.gallery
import zeit.content.image.interfaces
import zeit.crop.interfaces


class TestGalleryStorer(zeit.content.gallery.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        gallery = zeit.content.gallery.gallery.Gallery()
        gallery.image_folder = self.repository['2007']
        zeit.content.gallery.testing.add_image('2007', '01.jpg')
        zeit.content.gallery.testing.add_image('2007', '02.jpg')
        transaction.commit()
        gallery.reload_image_folder()
        self.gallery = gallery

    def test_store(self):
        entry = self.gallery['01.jpg']
        pil = PIL.Image.open(entry.image.open())
        zeit.crop.interfaces.IStorer(entry).store('10x10', pil)
        self.assertEqual(['01.jpg', '01-10x10.jpg', '02.jpg'], list(self.gallery.keys()))
        self.assertEqual(
            [True, False, False], [x.layout == 'hidden' for x in self.gallery.values()]
        )

        # A thumbnail for the scaled image was created
        thumbnail = self.gallery.image_folder['thumbnails']['01-10x10.jpg']
        thumbnail_data = thumbnail.open('r').read()

        # Images are overwritten
        pil = PIL.Image.open(self.gallery['02.jpg'].image.open())
        zeit.crop.interfaces.IStorer(entry).store('10x10', pil)
        self.assertEqual(['01.jpg', '01-10x10.jpg', '02.jpg'], list(self.gallery.keys()))
        self.assertEqual(
            [True, False, False], [x.layout == 'hidden' for x in self.gallery.values()]
        )

        # The thumbnail has been updated
        thumbnail = self.gallery.image_folder['thumbnails']['01-10x10.jpg']
        new_thumbnail_data = thumbnail.open('r').read()
        self.assertNotEqual(new_thumbnail_data, thumbnail_data)

    def test_metadata_from_source_image_is_copied(self):
        entry = self.gallery['01.jpg']
        metadata = zeit.content.image.interfaces.IImageMetadata(entry.image)
        self.assertEqual(
            ('ZEIT online', None, None, 'http://www.zeit.de', False), metadata.copyright
        )
        pil = PIL.Image.open(entry.image.open())
        zeit.crop.interfaces.IStorer(entry).store('10x10', pil)

        entry = self.gallery['01-10x10.jpg']
        metadata = zeit.content.image.interfaces.IImageMetadata(entry.image)
        self.assertEqual(
            ('ZEIT online', None, None, 'http://www.zeit.de', False), metadata.copyright
        )
