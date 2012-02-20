# Copyright (c) 2008-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import os
import re
import unittest
import zeit.cms.testing
import zope.testing.renormalizing


ObjectLogLayer = zeit.cms.testing.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'ObjectLogLayer', allow_teardown=True)


FORMATTED_DATE_REGEX = re.compile(r'\d{4} \d{1,2} \d{1,2}  \d\d:\d\d:\d\d')
checker = zope.testing.renormalizing.RENormalizing([
    (FORMATTED_DATE_REGEX, '<formatted date>')])


def test_suite():
    suite = unittest.TestSuite()
    test = zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        optionflags=(doctest.INTERPRET_FOOTNOTES | doctest.ELLIPSIS |
                     doctest.REPORT_NDIFF | doctest.NORMALIZE_WHITESPACE),
        checker=checker)
    test.layer = ObjectLogLayer
    suite.addTest(test)
    return suite
