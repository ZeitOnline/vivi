import zeit.cms.testing
import zeit.content.article.testing
import zeit.content.cp.testing

product_config = """\
<product-config zeit.arbeit>
</product-config>
"""


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml', product_config=(
        product_config +
        zeit.cms.testing.cms_product_config +
        zeit.content.article.testing.product_config +
        zeit.content.cp.testing.product_config
    ))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZCML_LAYER
