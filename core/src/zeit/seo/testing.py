import gocept.selenium

import zeit.cms.testing
import zeit.push.testing


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(zeit.push.testing.CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
CELERY_LAYER = zeit.cms.testing.CeleryWorkerLayer(bases=(ZOPE_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(CELERY_LAYER,))
HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = zeit.cms.testing.WebdriverLayer(name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,)
)


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):
    layer = WEBDRIVER_LAYER
