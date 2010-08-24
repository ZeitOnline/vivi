# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import doctest


def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        package='zeit.cms.workingcopy',
        optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
                     doctest.ELLIPSIS))
