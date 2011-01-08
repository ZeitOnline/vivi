# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing
import doctest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'form.txt',
        package='zeit.cms.browser',
        optionflags=zeit.cms.testing.optionflags))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'debug.txt',
        'error-views.txt',
        'listing.txt',
        'sourceedit.txt',
        'widget.txt',
        package='zeit.cms.browser'))
    return suite
