# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import unittest
import zeit.cms.testing
import zeit.content.article.tests
import zeit.content.cp.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'recension.txt',
        package='zeit.content.article.browser',
        layer=zeit.content.article.tests.ArticleLayer))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'layout.txt',
        package='zeit.content.article.browser',
        # we use the CDSLayer since it includes zeit.workflow which we need
        layer=zeit.content.article.tests.CDSLayer))
    return suite
