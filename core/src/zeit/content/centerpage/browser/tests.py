# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing
import zeit.content.centerpage.tests


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.content.centerpage.tests.CenterPageLayer))
    return suite
