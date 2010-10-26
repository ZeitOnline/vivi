# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing
import zeit.content.article.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'edit.image.txt',
        'edit.landing.txt',
        'edit.txt',
        'metadata.head.txt',
        'metadata.misc.txt',
        'metadata.navigation.txt',
        'metadata.texts.txt',
        'reference.gallery.txt',
        'reference.infobox.txt',
        package='zeit.content.article.edit.browser',
        layer=zeit.content.article.testing.ArticleLayer))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'edit.video.txt',
        package='zeit.content.article.edit.browser',
        layer=zeit.content.article.testing.ArticleBrightcoveLayer))
    return suite
