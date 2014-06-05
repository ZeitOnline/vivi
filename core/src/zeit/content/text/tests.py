# Copyright (c) 2007-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


TextLayer = zeit.cms.testing.ZCMLLayer('ftesting.zcml')


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=TextLayer)
