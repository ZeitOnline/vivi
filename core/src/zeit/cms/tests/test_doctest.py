# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import unittest
import zeit.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'content.txt',
        package='zeit.cms'
    ))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'async.txt',
        'cleanup.txt',
        'cmscontent.txt',
        package='zeit.cms'
    ))
    return suite
