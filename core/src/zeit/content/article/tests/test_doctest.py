import unittest
import zeit.cms.testing
import zeit.content.article.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'recension.txt',
        'layout.txt',
        package='zeit.content.article',
        layer=zeit.content.article.testing.LAYER))
    return suite
