# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.interfaces import ICMSContent
import zeit.cms.testing
import zeit.content.image.interfaces
import zeit.content.image.testing


class ImageAssetTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.image.testing.ImageLayer

    def test_IImages_accepts_IImage_for_backwards_compatibility(self):
        with self.assertNothingRaised():
            zeit.content.image.interfaces.IImages['image'].validate(
                ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG'))
