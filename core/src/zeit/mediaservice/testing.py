import zeit.cms.testing
import zeit.connector.testing
import zeit.content.article.testing


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'medienservice-folder': 'premium',
        'audio-folder': 'audio',
    },
    bases=zeit.content.article.testing.CONFIG_LAYER,
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    config_file='ftesting.zcml',
    features=['zeit.connector.sql'],
    bases=(CONFIG_LAYER, zeit.connector.testing.SQL_CONFIG_LAYER),
)
SQL_LAYER = zeit.connector.testing.SQLIsolationLayer(ZCML_LAYER)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(SQL_LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER
