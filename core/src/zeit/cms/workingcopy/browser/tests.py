# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.cms.workingcopy.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.cms.workingcopy.testing.layer,
        )
