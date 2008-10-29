# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import re
import os
import unittest

import zope.testing.renormalizing
from zope.testing import doctest

import zope.app.testing.functional

import zeit.cms.testing
import zeit.wysiwyg.test


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'filebrowser.txt',
        layer=zeit.wysiwyg.test.WYSIWYGLayer))
    return suite
