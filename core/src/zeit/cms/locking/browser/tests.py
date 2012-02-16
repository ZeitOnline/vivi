# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import re
import unittest
import zeit.cms.testing
import zope.testing.renormalizing


checker = zope.testing.renormalizing.RENormalizing([
    (re.compile(r'\d{4} \d{1,2} \d{1,2}  \d\d:\d\d:\d\d'), '<FORMATTED DATE>')
])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
                     doctest.ELLIPSIS + doctest.INTERPRET_FOOTNOTES),
        checker=checker))
    return suite
