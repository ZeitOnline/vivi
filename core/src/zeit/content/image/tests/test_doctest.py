# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.content.image.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'syndication.txt',
        'syndication2.txt',
        'transform.txt',
        'masterimage.txt',
        package='zeit.content.image',
        layer=zeit.content.image.testing.ImageLayer)
