# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.testing import copy_inherited_functions
import unittest
import zeit.cms.content.tests.test_contentsource
import zeit.cms.testing
import zeit.content.gallery.interfaces
import zeit.content.gallery.testing
import zope.interface.exceptions


class TestGallerySource(
    zeit.cms.content.tests.test_contentsource.ContentSourceBase,
    zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.gallery.testing.GalleryLayer

    source = zeit.content.gallery.interfaces.gallerySource
    expected_types = ['gallery']

    copy_inherited_functions(
        zeit.cms.content.tests.test_contentsource.ContentSourceBase,
        locals())


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
