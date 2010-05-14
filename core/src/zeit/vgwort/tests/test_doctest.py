# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.vgwort.testing


def test_suite():
    return zeit.vgwort.testing.FunctionalDocFileSuite(
        'README.txt',
        package='zeit.vgwort')
