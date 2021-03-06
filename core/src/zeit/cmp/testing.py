import pkg_resources
import zeit.cms.testing


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer({
    'vendors': 'file://' + pkg_resources.resource_filename(
        __name__, 'tests/fixtures/vendors.xml')
}, bases=(zeit.cms.testing.CONFIG_LAYER,))


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZOPE_LAYER
