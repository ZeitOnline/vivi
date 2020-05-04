import pkg_resources
import zeit.cms.testing

product_config = """\
<product-config zeit.wochenmarkt>
  categories-url file://{base}/tests/fixtures/categories.xml
  ingredients-url file://{base}/tests/fixtures/ingredients.xml
</product-config>
""".format(
    base=pkg_resources.resource_filename(__name__, ''))

CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    product_config, bases=(zeit.cms.testing.CONFIG_LAYER,))
ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting.zcml', bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZOPE_LAYER
