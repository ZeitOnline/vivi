# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.brightcove.testing


def test_suite():
    return zeit.brightcove.testing.FunctionalDocFileSuite(
        'asset.txt',
        'browser.txt',
        'checkout.txt',
        'reference.txt',
        package='zeit.brightcove')
