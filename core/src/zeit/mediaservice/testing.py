import zeit.cms.testing
import zeit.connector.testing
import zeit.content.article.testing


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'medienservice-folder': 'premium',
        'audio-folder': 'audio',
    },
    bases=(zeit.content.article.testing.CONFIG_LAYER,),
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))

SQL_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    features=['zeit.connector.sql'],
    bases=(CONFIG_LAYER, zeit.connector.testing.SQL_CONFIG_LAYER),
)
SQL_ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(SQL_ZCML_LAYER,))
SQL_CONNECTOR_LAYER = zeit.connector.testing.SQLDatabaseLayer(bases=(SQL_ZOPE_LAYER,))


class SQLTestCase(zeit.connector.testing.TestCase):
    layer = SQL_CONNECTOR_LAYER


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER
