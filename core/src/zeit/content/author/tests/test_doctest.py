# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.author.testing


def test_suite():
    return zeit.content.author.testing.FunctionalDocFileSuite(
        'README.txt',
        package='zeit.content.author')
