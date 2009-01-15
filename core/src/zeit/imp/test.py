# coding: utf8
# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import pkg_resources
import unittest
import zeit.cms.testing
import zeit.imp.interfaces
import zeit.imp.mask
import zeit.imp.source
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


class TestScaleSource(zope.app.testing.functional.BrowserTestCase):

    layer = imp_layer

    def setUp(self):
        scale_xml_path = pkg_resources.resource_filename(
            __name__, 'scales.xml')
        zeit.cms.testing.setup_product_config(
            {'zeit.imp': {'scale-source': 'file://%s' % scale_xml_path}})
        self.source = zeit.imp.source.ScaleSource()

    def test_scale_source(self):
        scales = list(self.source)
        self.assertEquals(7, len(scales))
        scale = scales[0]
        self.assertEquals('450x200', scale.name)
        self.assertEquals('450', scale.width)
        self.assertEquals('200', scale.height)
        self.assertEquals(u'Aufmacher groß (450×200)', scale.title)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLayerMask))
    suite.addTest(unittest.makeSuite(TestScaleSource))
    return suite
