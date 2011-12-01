# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'delete.txt',
        'file.txt',
        'rename.txt',
        'tree.txt',
        package='zeit.cms.repository.browser')
