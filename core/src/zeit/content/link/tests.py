# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.push


layer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=(zeit.cms.testing.cms_product_config
                    + zeit.push.product_config))


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=layer)
