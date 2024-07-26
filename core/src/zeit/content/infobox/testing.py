import zeit.cms.testing
import zeit.connector.testing


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    bases=(zeit.cms.testing.CONFIG_LAYER, zeit.connector.testing.SQL_CONFIG_LAYER)
)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
DB_LAYER = zeit.connector.testing.SQLDatabaseLayer(bases=(ZOPE_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(DB_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER
