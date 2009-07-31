# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import PIL
import zeit.cms.testing
import zeit.content.gallery.gallery
import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.imp.interfaces
import zope.component


class TestGalleryStorer(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.gallery.testing.GalleryLayer

    def setUp(self):
        super(TestGalleryStorer, self).setUp()
        gallery = zeit.content.gallery.gallery.Gallery()
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        gallery.image_folder = repository['2007']
        zeit.content.gallery.testing.add_image('2007', '01.jpg')
        zeit.content.gallery.testing.add_image('2007', '02.jpg')
        gallery.reload_image_folder()
        self.gallery = gallery

    def test_store(self):
        entry = self.gallery['01.jpg']
        pil = PIL.Image.open(entry.image.open())
        zeit.imp.interfaces.IStorer(entry).store('10x10', pil)
        self.assertEqual(['01.jpg', '01-10x10.jpg', '02.jpg'],
                         list(self.gallery.keys()))
        self.assertEqual([True, False, False], [
            x.layout == 'hidden' for x in self.gallery.values()])

        # Images are overwritten
        pil = PIL.Image.open(entry.image.open())
        zeit.imp.interfaces.IStorer(entry).store('10x10', pil)
        self.assertEqual(['01.jpg', '01-10x10.jpg', '02.jpg'],
                         list(self.gallery.keys()))

    def test_metadata_from_source_image_is_copied(self):
        entry = self.gallery['01.jpg']
        metadata = zeit.content.image.interfaces.IImageMetadata(entry.image)
        self.assertEquals(
            ((u'ZEIT online', u'http://www.zeit.de'),),
            metadata.copyrights)
        pil = PIL.Image.open(entry.image.open())
        zeit.imp.interfaces.IStorer(entry).store('10x10', pil)

        entry = self.gallery['01-10x10.jpg']
        metadata = zeit.content.image.interfaces.IImageMetadata(entry.image)
        self.assertEquals(
            ((u'ZEIT online', u'http://www.zeit.de'),),
            metadata.copyrights)
