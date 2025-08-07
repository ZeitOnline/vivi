from zeit.cms.testing.sql import GCS_SERVER_LAYER
import zeit.cms.checkout
import zeit.cms.testing
import zeit.content.article.testing


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'storage-project': 'ignored_by_emulator',
        'storage-bucket': GCS_SERVER_LAYER.bucket,
    },
    bases=zeit.content.article.testing.CONFIG_LAYER,
)


ZCML_LAYER = zeit.cms.testing.ZCMLLayer((CONFIG_LAYER, GCS_SERVER_LAYER))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER
