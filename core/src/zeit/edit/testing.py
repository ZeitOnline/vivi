import zeit.cms.testing


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(zeit.cms.testing.CONFIG_LAYER)
_zope_layer = zeit.cms.testing.RawZopeLayer(ZCML_LAYER)
ZOPE_LAYER = zeit.cms.testing.SQLIsolationSavepointLayer(_zope_layer)
WSGI_LAYER = zeit.cms.testing.WSGILayer(ZOPE_LAYER)
HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(
    zeit.cms.testing.WSGILayer(zeit.cms.testing.SQLIsolationTruncateLayer(_zope_layer))
)
WEBDRIVER_LAYER = zeit.cms.testing.WebdriverLayer(HTTP_LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):
    layer = WEBDRIVER_LAYER
    skin = 'vivi'
