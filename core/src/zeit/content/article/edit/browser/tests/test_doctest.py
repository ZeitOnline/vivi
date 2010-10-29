# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing
import zeit.content.article.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'edit.landing.txt',
        'edit.txt',
        'edit.related.txt',
        'metadata.head.txt',
        'metadata.misc.txt',
        'metadata.navigation.txt',
        'metadata.texts.txt',
        package='zeit.content.article.edit.browser',
        layer=zeit.content.article.testing.ArticleLayer))
    return suite
