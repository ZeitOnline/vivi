# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import os
import unittest

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


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'html.txt',
        optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
                     doctest.ELLIPSIS)))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=ArticleLayer))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'syndication.txt',
        layer=ArticleSyndicationLayer))
    return suite
