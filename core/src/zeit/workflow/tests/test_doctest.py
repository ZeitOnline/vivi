# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.workflow.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'dependency.txt',
        'syndication.txt',
        layer=zeit.workflow.testing.LAYER,
        package='zeit.workflow')
