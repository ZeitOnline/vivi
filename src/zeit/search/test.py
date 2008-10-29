# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import os
import unittest

from zope.testing import doctest

import zope.app.testing.functional

import zeit.cms.testing


test_data_dir = os.path.join(os.path.dirname(__file__), 'testdata')

product_config = {
    'zeit.search': {
        'xapian-url': 'file://%s' % os.path.join(
            test_data_dir, 'xapian-test.xml'),
        'dwds-url': 'file://%s' % os.path.join(
            test_data_dir, 'dwds-test.xml'),
        'lucene-url': 'file://%s' % os.path.join(
            test_data_dir, 'lucene-test.xml'),
    }
}


SearchLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'SearchLayer', allow_teardown=True)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'lucene.txt',
        product_config=product_config))
    return suite
