# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import os
import unittest
import zeit.cms.testing
import zeit.content.portraitbox.tests
import zope.app.testing.functional


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.content.portraitbox.tests.PortraitboxLayer))
    return suite
