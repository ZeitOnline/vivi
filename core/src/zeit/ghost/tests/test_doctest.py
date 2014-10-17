# Copyright (c) 2007-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.ghost.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        package='zeit.ghost',
        layer=zeit.ghost.testing.ZCML_LAYER)
