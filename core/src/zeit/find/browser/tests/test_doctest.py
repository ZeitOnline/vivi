# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing
import zeit.find.tests


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        package='zeit.find.browser',
        layer=zeit.find.tests.SearchLayer))
    return suite

