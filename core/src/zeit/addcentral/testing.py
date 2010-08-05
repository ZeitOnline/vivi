# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import gocept.selenium.ztk


layer = zeit.cms.testing.ZCMLLayer('ftesting.zcml', product_config=True)
selenium_layer  = gocept.selenium.ztk.Layer(layer)


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('layer', layer)
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = layer
