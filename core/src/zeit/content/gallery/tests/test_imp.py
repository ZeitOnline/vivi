# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import PIL
import zeit.cms.testing
import zeit.content.gallery.gallery
import zeit.content.gallery.interfaces
import zeit.imp.interfaces
import zope.component


class TestGalleryStorer(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.gallery.testing.GalleryLayer

    def test_store(self):
        gallery = zeit.content.gallery.gallery.Gallery()
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        gallery.image_folder = repository['2007']
        zeit.content.gallery.testing.add_image('2007', '01.jpg')
        zeit.content.gallery.testing.add_image('2007', '02.jpg')
        gallery.reload_image_folder()

        entry = gallery['01.jpg']
        pil = PIL.Image.open(entry.image.open())
        zeit.imp.interfaces.IStorer(entry).store('10x10', pil)
        self.assertEqual(['01.jpg', '01-10x10.jpg', '02.jpg'],
                         list(gallery.keys()))
        self.assertEqual([True, False, False], [
            x.layout == 'hidden' for x in gallery.values()])

        # Images are not overwritten
        pil = PIL.Image.open(entry.image.open())
        zeit.imp.interfaces.IStorer(entry).store('10x10', pil)
        self.assertEqual(['01.jpg', '01-10x10.jpg', '02.jpg'],
                         list(gallery.keys()))
