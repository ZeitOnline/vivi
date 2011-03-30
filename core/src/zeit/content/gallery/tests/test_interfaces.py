# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.content.tests.test_contentsource
import zeit.content.gallery.interfaces
import zeit.content.gallery.testing
import zope.interface.exceptions


class TestGallerySource(
    zeit.cms.content.tests.test_contentsource.ContentSourceTest):

    layer = zeit.content.gallery.testing.GalleryLayer

    source = zeit.content.gallery.interfaces.gallerySource
    expected_types = ['gallery']


class MaxLengthTest(unittest.TestCase):

    def setUp(self):
        self.dummy = type('dummy', (object,), {})()

    def test_shorter_than_limit_passes(self):
        from zeit.content.gallery.interfaces import IMaxLengthHTMLContent
        from zeit.content.gallery.interfaces import GALLERY_TEXT_MAX_LENGTH
        self.dummy.html = '<p><b>%s</b></p>' % ('a' * GALLERY_TEXT_MAX_LENGTH)
        IMaxLengthHTMLContent.validateInvariants(self.dummy)

    def test_longer_than_limit_raises(self):
        from zeit.content.gallery.interfaces import IMaxLengthHTMLContent
        from zeit.content.gallery.interfaces import GALLERY_TEXT_MAX_LENGTH
        self.dummy.html = '<p><b>%s</b></p>' % (
            'a' * (GALLERY_TEXT_MAX_LENGTH + 1))
        self.assertRaises(
            zope.schema.ValidationError,
            lambda: IMaxLengthHTMLContent.validateInvariants(self.dummy))
