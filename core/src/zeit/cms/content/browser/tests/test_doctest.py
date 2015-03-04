import doctest
import unittest
import zeit.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'form.txt',
        'template.txt',
        'typechange.txt',
        'widget-subnav.txt',
        package='zeit.cms.content.browser'))
    suite.addTest(doctest.DocFileSuite(
        'widget.txt',
        optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
                     doctest.ELLIPSIS),
        package='zeit.cms.content.browser'))
    return suite
