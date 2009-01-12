# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import pkg_resources
import unittest
import zeit.imp.mask
import zope.app.testing.functional


imp_layer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'ImpLayer', allow_teardown=True)


class TestLayerMask(unittest.TestCase):

    def test_mask(self):
        # Create a 20x30 mask in an 150x100 image
        mask = zeit.imp.mask.Mask((150, 100), (20, 30))
        mask_data = mask.open('r').read()
        expected_data = pkg_resources.resource_string(
            __name__, 'test_mask.png')
        self.assertEquals(expected_data, mask_data,
                          "Mask doesn't match expected mask.")

    def test_mask_with_border(self):
        # Create a 20x30 mask in an 150x100 image
        mask = zeit.imp.mask.Mask((150, 100), (20, 30), border=True)
        mask_data = mask.open('r').read()
        expected_data = pkg_resources.resource_string(
            __name__, 'test_mask_border.png')
        self.assertEquals(expected_data, mask_data,
                          "Mask doesn't match expected mask.")

    def test_rect_box(self):
        mask = zeit.imp.mask.Mask((150, 100), (20, 30))
        self.assertEquals(((65, 35), (85, 65)), mask._get_rect_box())



def test_suite():
    suite = unittest.TestSuite(
        unittest.makeSuite(TestLayerMask))
    return suite
