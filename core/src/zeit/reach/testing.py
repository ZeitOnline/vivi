import zeit.cms.testing


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {'freeze-now': ''}, bases=zeit.cms.testing.CONFIG_LAYER
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(CONFIG_LAYER, features=['zeit.connector.sql.zope'])
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)

HTTP_LAYER = zeit.cms.testing.HTTPLayer()
LAYER = zeit.cms.testing.Layer((ZOPE_LAYER, HTTP_LAYER))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = LAYER
