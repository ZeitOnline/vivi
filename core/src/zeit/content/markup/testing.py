import zeit.cms.testing


ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting.zcml', bases=(zeit.cms.testing.CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.ZeitCmsBrowserTestCase):
    layer = WSGI_LAYER
