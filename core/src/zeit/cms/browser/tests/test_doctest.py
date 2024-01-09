import doctest
import unittest

import zeit.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        doctest.DocFileSuite(
            'form.txt', package='zeit.cms.browser', optionflags=zeit.cms.testing.optionflags
        )
    )
    suite.addTest(
        zeit.cms.testing.FunctionalDocFileSuite(
            'README.txt',
            'error-views.txt',
            'listing.txt',
            'sourceedit.txt',
            'widget.txt',
            package='zeit.cms.browser',
        )
    )
    return suite
