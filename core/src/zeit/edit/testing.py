import zeit.cms.testing


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(zeit.cms.testing.CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))
HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(bases=(WSGI_LAYER,))
WEBDRIVER_LAYER = zeit.cms.testing.WebdriverLayer(bases=(HTTP_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):
    layer = WEBDRIVER_LAYER
    skin = 'vivi'
