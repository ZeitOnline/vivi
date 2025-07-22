import zeit.cms.testing
import zeit.connector.testing


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {'medienservice-folder': 'premium', 'audio-folder': 'audio'},
    bases=(zeit.cms.testing.CONFIG_LAYER,),
)

SQL_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    features=['zeit.connector.sql'],
    bases=(CONFIG_LAYER, zeit.connector.testing.SQL_CONFIG_LAYER),
)
SQL_ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(SQL_ZCML_LAYER,))
SQL_CONNECTOR_LAYER = zeit.connector.testing.SQLDatabaseLayer(bases=(SQL_ZOPE_LAYER,))


class SQLTestCase(zeit.connector.testing.TestCase):
    layer = SQL_CONNECTOR_LAYER
