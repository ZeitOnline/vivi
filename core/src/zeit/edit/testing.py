# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.selenium.ztk
import zeit.cms.testing


ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting.zcml')
SELENIUM_LAYER = gocept.selenium.ztk.Layer(ZCML_LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZCML_LAYER


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):

    layer = SELENIUM_LAYER
    skin = 'vivi'
