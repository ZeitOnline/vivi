import plone.testing
import zeit.cms.testing
import zeit.retresco.testhelper
import zeit.retresco.testing


product_config = """
<product-config zeit.reach>
    url http://localhost:{port}
    freeze-now
</product-config>
"""

CONFIG_LAYER = zeit.retresco.testing.ProductConfigLayer(
    product_config, package='zeit.reach', bases=(
        zeit.retresco.testing.CONFIG_LAYER,))
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
LAYER = plone.testing.Layer(name='Layer', bases=(
    ZOPE_LAYER,
    zeit.retresco.testhelper.ELASTICSEARCH_MOCK_LAYER,
    zeit.retresco.testhelper.TMS_MOCK_LAYER))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = LAYER
