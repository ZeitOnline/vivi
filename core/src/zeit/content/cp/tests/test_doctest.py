import unittest
import zeit.content.cp
import zeit.content.cp.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.content.cp.testing.FunctionalDocFileSuite(
        'README.txt',
        'cmscontentiterable.txt',
        'rule.txt',
        'teaser.txt',
        package=zeit.content.cp))
    suite.addTest(zeit.content.cp.testing.FunctionalDocFileSuite(
        'feed.txt',
        layer=zeit.content.cp.testing.FEED_SERVER_LAYER,
        globs=dict(layer=zeit.content.cp.testing.FEED_SERVER_LAYER),
        package=zeit.content.cp))
    return suite
