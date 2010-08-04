# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


layer = zeit.cms.testing.ZCMLLayer('ftesting.zcml', product_config=True)


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('layer', layer)
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = layer
