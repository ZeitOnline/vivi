# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.browser.listing
import zeit.cms.testing
from zope.testing import doctest


class HitColumnTest(unittest.TestCase):

    def test_sort_key(self):

        class TestAccessCounter(object):
            hits = 5
            total_hits = 19

        column = zeit.cms.browser.listing.HitColumn(
            getter=lambda i, f: i)
        self.assertEquals((19, 5),
                          column.getSortKey(TestAccessCounter(),
                                            formatter=None))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'form.txt',
        optionflags=zeit.cms.testing.optionflags))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'debug.txt',
        'error-views.txt',
        'listing.txt',
        'sourceedit.txt',
        'widget.txt'))
    suite.addTest(unittest.makeSuite(HitColumnTest))
    return suite
