# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing
import zeit.content.article.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'edit.image.txt',
        'edit.landing.txt',
        'edit.txt',
        'metadata.head.txt',
        'metadata.navigation.txt',
        'recension.txt',
        package='zeit.content.article.browser',
        layer=zeit.content.article.testing.ArticleLayer))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'layout.txt',
        package='zeit.content.article.browser',
        # we use the CDSLayer since it includes zeit.workflow which we need
        layer=zeit.content.article.testing.CDSLayer))
    return suite
