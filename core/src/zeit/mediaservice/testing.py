import zeit.cms.testing
import zeit.content.article.testing


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'medienservice-folder': 'premium',
        'audio-folder': 'audio',
        'client-id': 'client-id',
        'client-secret': 'client-secret',
        'discovery-url': 'https://discovery-url.foo',
    },
    bases=zeit.content.article.testing.CONFIG_LAYER,
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(CONFIG_LAYER, features=['zeit.connector.sql'])
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER
