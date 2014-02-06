# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.httpserverlayer.wsgi
import gocept.selenium
import zeit.cms.testing


ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting.zcml', product_config=True)
WSGI_LAYER = zeit.cms.testing.WSGILayer(name='WSGILayer', bases=(ZCML_LAYER,))
HTTP_LAYER = gocept.httpserverlayer.wsgi.Layer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = gocept.selenium.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
SELENIUM_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='SeleniumLayer', bases=(WD_LAYER,))
