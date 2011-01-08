# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing


ImageLayer = zeit.cms.testing.ZCMLLayer( 'ftesting.zcml', product_config=True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=ImageLayer))
    return suite
