# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest

import zeit.cms.testing

import zeit.content.rawxml.test


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.content.rawxml.test.RawXMLLayer))
    return suite
