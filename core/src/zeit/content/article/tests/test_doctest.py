# Copyright (c) 2007-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import __future__
import unittest
import zeit.cms.testing
import zeit.content.article.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'recension.txt',
        package='zeit.content.article',
        layer=zeit.content.article.testing.ArticleLayer))

    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'cds_export.txt',
        'cds_import.txt',
        'layout.txt',
        package='zeit.content.article',
        layer=zeit.content.article.testing.CDSLayer,
        checker=zeit.content.article.testing.checker,
        globs={'with_statement': __future__.with_statement}))
    return suite
