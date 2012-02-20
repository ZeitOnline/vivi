# Copyright (c) 2008-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import doctest
import os
import unittest
import zeit.cms.testing


invalidate_layer = zeit.cms.testing.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'InvalidateLayer', allow_teardown=True)


def test_suite():
    suite = unittest.TestSuite()
    test = zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
                     doctest.ELLIPSIS))
    test.layer = invalidate_layer
    suite.addTest(test)
    return suite
