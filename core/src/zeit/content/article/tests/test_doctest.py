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
        layer=zeit.content.article.testing.LAYER))

    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'cds_export.txt',
        'cds_import.txt',
        'layout.txt',
        package='zeit.content.article',
        layer=zeit.content.article.testing.CDS_LAYER,
        checker=zeit.content.article.testing.checker,
        globs={'with_statement': __future__.with_statement}))
    return suite
