# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import os
import re
import unittest
import zeit.cms.testing
import zeit.wysiwyg.tests
import zope.app.testing.functional
import zope.testing.renormalizing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'filebrowser.txt',
        layer=zeit.wysiwyg.tests.WYSIWYGLayer))
    return suite
