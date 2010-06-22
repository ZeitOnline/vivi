# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.ghost.tests


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'checkin.txt',
        layer=zeit.ghost.tests.GhostLayer,
        )
