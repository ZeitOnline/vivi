import zeit.cms.testing
import zeit.push.testing


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(zeit.push.testing.CONFIG_LAYER)
_zope_layer = zeit.cms.testing.RawZopeLayer(ZCML_LAYER)
ZOPE_LAYER = zeit.cms.testing.SQLIsolationTruncateLayer(_zope_layer)
CELERY_LAYER = zeit.cms.testing.CeleryWorkerLayer(ZOPE_LAYER)
WSGI_LAYER = zeit.cms.testing.WSGILayer(CELERY_LAYER)
HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(WSGI_LAYER)
WEBDRIVER_LAYER = zeit.cms.testing.WebdriverLayer(HTTP_LAYER)


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):
    layer = WEBDRIVER_LAYER
