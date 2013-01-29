# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.video.testing


def test_suite():
    return zeit.content.video.testing.FunctionalDocFileSuite(
        'asset.txt',
        'video.txt',
        package='zeit.content.video')
