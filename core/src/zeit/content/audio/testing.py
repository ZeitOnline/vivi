import importlib.resources

import zeit.cms.testing


product_config = """
<product-config zeit.content.audio>
   podcast-source file://{here}/tests/fixtures/podcasts.xml
</product-config>
""".format(here=importlib.resources.files(__package__))

CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    product_config, bases=(zeit.cms.testing.CONFIG_LAYER,)
)

ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting.zcml', bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER
