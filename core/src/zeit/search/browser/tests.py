# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import os
import unittest
import zeit.search.tests


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.search.tests.SearchLayer,
        product_config=zeit.search.tests.product_config))
    return suite
