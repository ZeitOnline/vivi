# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.addcentral
import zeit.addcentral.testing


def test_suite():
    return zeit.addcentral.testing.FunctionalDocFileSuite(
        'README.txt',
        package=zeit.addcentral)
