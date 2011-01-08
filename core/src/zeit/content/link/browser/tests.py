# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import os
import unittest
import zeit.cms.testing
import zeit.content.link.tests


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.content.link.tests.ImageLayer))
    return suite
