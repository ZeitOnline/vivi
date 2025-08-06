import zeit.cms.testing
import zeit.retresco.testing


HTTP_LAYER = zeit.cms.testing.HTTPLayer()
CONFIG_LAYER = zeit.retresco.testing.ProductConfigLayer(
    {
        'url': 'http://localhost:{port}',
        'freeze-now': '',
    },
    package='zeit.reach',
    bases=(
        HTTP_LAYER,
        zeit.cms.testing.CONFIG_LAYER,
    ),
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(CONFIG_LAYER)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER
