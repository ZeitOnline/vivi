# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest

from zope.testing import doctest

import zeit.cms.testing

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'form.txt',
        optionflags=zeit.cms.testing.optionflags))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'debug.txt',
        'error-views.txt',
        'listing.txt',
        'sourceedit.txt',
        'widget.txt'))
    return suite
