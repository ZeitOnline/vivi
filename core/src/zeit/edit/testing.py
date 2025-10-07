import zeit.cms.testing


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    zeit.cms.testing.CONFIG_LAYER, features=['zeit.connector.sql.zope']
)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)
WSGI_LAYER = zeit.cms.testing.WSGILayer(ZOPE_LAYER)
HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(WSGI_LAYER)
WEBDRIVER_LAYER = zeit.cms.testing.WebdriverLayer(HTTP_LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):
    layer = WEBDRIVER_LAYER
    skin = 'vivi'
