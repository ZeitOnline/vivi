# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import os.path
import unittest
import zeit.imp.mask
import zope.app.testing.functional


imp_layer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'ImpLayer', allow_teardown=True)


class TestLayerMask(unittest.TestCase):

    def test_mask(self):
        # Create a 20x30 mask in an 150x100 image
        mask = zeit.imp.mask.Mask((150, 100), (20, 30))
        mask_data = mask.open('r').read()
        expected_data = open(os.path.join(
            os.path.dirname(__file__), 'test_mask.png')).read()
        open('/tmp/foomask_data.png', 'w').write(mask_data)
        self.assertEquals(expected_data, mask_data,
                          "Mask doesn't match expected mask.")

    def test_rect_box(self):
        mask = zeit.imp.mask.Mask((150, 100), (20, 30))
        self.assertEquals(((65, 35), (85, 65)), mask._get_rect_box())



def test_suite():
    suite = unittest.TestSuite(
        unittest.makeSuite(TestLayerMask))
    return suite
