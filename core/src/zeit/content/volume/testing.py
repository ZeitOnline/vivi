# coding: utf-8
import pkg_resources
import zeit.cms.testing
import zeit.content.image.testing

product_config = """
<product-config zeit.content.volume>
    volume-cover-source file://{here}/tests/fixtures/volume-covers.xml
    dav-archive-url http://cms-backend.zeit.de:9000/cms/archiv-wf/archiv/
</product-config>
<product-config zeit.connector>
    repository-path {here}/browser/tests/testcontent
</product-config>
""".format(here=pkg_resources.resource_filename(__name__, '.'))


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml', product_config=(
        product_config +
        zeit.cms.testing.cms_product_config +
        zeit.content.image.testing.product_config))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZCML_LAYER
