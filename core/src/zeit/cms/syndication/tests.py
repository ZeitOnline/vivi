# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest

from zope.testing import doctest

import zeit.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'feed.txt',
        'oldchannel.txt',
        optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
                     doctest.ELLIPSIS + doctest.INTERPRET_FOOTNOTES)))
    return suite
