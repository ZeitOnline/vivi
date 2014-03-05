# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


layer = zeit.cms.testing.ZCMLLayer('ftesting.zcml', product_config=True)


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=layer)
