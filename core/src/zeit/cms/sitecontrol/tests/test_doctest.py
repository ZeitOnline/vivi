# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        package='zeit.cms.sitecontrol')

