# coding: utf-8
import pkg_resources
import re
import zeit.cms.testing
import zeit.content.image.testing


product_config = """
<product-config zeit.content.volume>
    volume-cover-source file://{here}/tests/fixtures/volume-covers.xml
</product-config>
""".format(here=pkg_resources.resource_filename(__name__, '.'))


# We need a `products.xml` config with `volume="true"` attributes for filtering
cms_product_config = re.sub(
    'source-products file://.*/products.xml',
    'source-products file://{here}/tests/fixtures/products.xml'.format(
        here=pkg_resources.resource_filename(__name__, '.')),
    zeit.cms.testing.cms_product_config)


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml', product_config=(
        product_config +
        cms_product_config +
        zeit.content.image.testing.product_config))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZCML_LAYER
