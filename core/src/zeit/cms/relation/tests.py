# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import re
import os
import unittest

from zope.testing import doctest

import zeit.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite('README.txt'))
    return suite
