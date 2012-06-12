# Copyright (c) 2008-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import zeit.objectlog.testing
import zope.app.testing.functional


def test_suite():
    suite = zope.app.testing.functional.FunctionalDocFileSuite(
        'README.txt',
        package='zeit.objectlog',
        optionflags=(doctest.INTERPRET_FOOTNOTES | doctest.ELLIPSIS |
                     doctest.REPORT_NDIFF | doctest.NORMALIZE_WHITESPACE),
        checker=zeit.objectlog.testing.checker)
    suite.layer = zeit.objectlog.testing.ObjectLogLayer
    return suite
