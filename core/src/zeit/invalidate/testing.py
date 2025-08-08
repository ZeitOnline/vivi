import zeit.cms.testing


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(zeit.cms.testing.CONFIG_LAYER)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)
WSGI_LAYER = zeit.cms.testing.WSGILayer(ZOPE_LAYER)
