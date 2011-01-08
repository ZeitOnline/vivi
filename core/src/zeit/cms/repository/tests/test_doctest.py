# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import unittest
import zeit.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'cache.txt',
        'preference.txt',
        'file.txt',
        package='zeit.cms.repository'))
    return suite
