# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.tests.test_contentsource
import zeit.content.gallery.interfaces
import zeit.content.gallery.testing


class TestGallerySource(
    zeit.cms.content.tests.test_contentsource.ContentSourceTest):

    layer = zeit.content.gallery.testing.GalleryLayer

    source = zeit.content.gallery.interfaces.gallerySource
    expected_types = ['gallery']
