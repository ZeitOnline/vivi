# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.testing


def test_suite():
    return zeit.content.cp.testing.FunctionalDocFileSuite(
        'cpextra.txt',
        'teaser.txt',
        'teaser-two-column-layout.txt',
        'teaser-teasergroup-support.txt',
        'xml.txt',
        package=zeit.content.cp.blocks,
    )
