# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest2 as unittest  # XXX
import zeit.brightcove.testing


def test_suite():
    return unittest.skip('not yet')(
        zeit.brightcove.testing.FunctionalDocFileSuite(
        'asset.txt',
        'browser.txt',
        'reference.txt',
        package='zeit.brightcove')
        )
