import pkg_resources
import plone.testing
import zeit.cms.testing
import zeit.push.testing


product_config = """
<product-config zeit.content.link>
    source-blogs file://%s
</product-config>
""" % pkg_resources.resource_filename(__name__, 'blog_source.xml')


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=(zeit.cms.testing.cms_product_config +
                    zeit.push.testing.product_config +
                    product_config))

PUSH_LAYER = zeit.push.testing.UrbanairshipTemplateLayer(
    name='UrbanairshipTemplateLayer', bases=(ZCML_LAYER,))

LAYER = plone.testing.Layer(bases=(PUSH_LAYER,), name='LinkLayer')
