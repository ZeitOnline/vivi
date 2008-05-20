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


ArticleLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'ArticleLayer', allow_teardown=True)


# We define a seperate layer for syndication because the checkin/checkout
# manager is overridden for the syndication test
ArticleSyndicationLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'ArticleSyndicationLayer', allow_teardown=True)


ISO8601_REGEX = re.compile(
    r"(?P<year>[0-9]{4})(-(?P<month>[0-9]{1,2})(-(?P<day>[0-9]{1,2})"
    r"((?P<separator>.)(?P<hour>[0-9]{2}):(?P<minute>[0-9]{2})(:(?P<second>[0-9]{2})(\.(?P<fraction>[0-9]+))?)?"
    r"(?P<timezone>Z|(([-+])([0-9]{2}):([0-9]{2})))?)?)?)?")


checker = zope.testing.renormalizing.RENormalizing([
  (ISO8601_REGEX, '<iso8601 date>')])



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'recension.txt',
        optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
                     doctest.ELLIPSIS + doctest.INTERPRET_FOOTNOTES),
        layer=ArticleLayer))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'syndication.txt',
        layer=ArticleSyndicationLayer,
        checker=checker))
    return suite
