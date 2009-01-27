# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import os
import unittest
import zeit.search.test
from zope.testing import doctest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.search.test.SearchLayer,
        product_config=zeit.search.test.product_config))
    return suite
