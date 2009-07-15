# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing
import zeit.content.gallery.tests


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'imp.txt',
        product_config=zeit.content.gallery.tests.product_config,
        layer=zeit.content.gallery.tests.GalleryLayer))
    return suite
