import unittest
import zeit.cms.testing
import zeit.content.gallery.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'reference.txt',
        package='zeit.content.gallery',
        layer=zeit.content.gallery.testing.ZOPE_LAYER))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'workflow.txt',
        package='zeit.content.gallery',
        layer=zeit.content.gallery.testing.WORKFLOW_LAYER))
    return suite
