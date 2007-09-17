# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

from zope.testing import doctest


def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
                     doctest.ELLIPSIS))
