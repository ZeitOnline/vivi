import importlib.resources
import plone.testing
import zeit.cms.testing
import zeit.push.testing


product_config = """
<product-config zeit.content.link>
    source-blogs file://{here}/blog_source.xml
</product-config>
""".format(here=importlib.resources.files(__package__))


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    product_config, bases=(zeit.push.testing.CONFIG_LAYER,)
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
PUSH_LAYER = zeit.push.testing.UrbanairshipTemplateLayer(
    name='UrbanairshipTemplateLayer', bases=(ZOPE_LAYER,)
)
LAYER = plone.testing.Layer(bases=(PUSH_LAYER,), name='Layer')
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER
