import doctest
import unittest
import zeit.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'form.txt',
        'template.txt',
        'typechange.txt',
        'widget.txt',
        'widget-subnav.txt',
        package='zeit.cms.content.browser'))
    return suite
