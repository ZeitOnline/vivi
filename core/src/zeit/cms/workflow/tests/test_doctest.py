# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import unittest
import zeit.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'mock.txt',
        package='zeit.cms.workflow',
        optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
                     doctest.ELLIPSIS)))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'modified.txt',
        'status.txt',
        package='zeit.cms.workflow',
        ))
    return suite
