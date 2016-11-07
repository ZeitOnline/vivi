import zeit.cms.testing
import zeit.push
import pkg_resources


product_config = """
<product-config zeit.content.link>
    source-blogs file://%s
</product-config>
""" % pkg_resources.resource_filename(__name__, 'blog_source.xml')


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=(zeit.cms.testing.cms_product_config +
                    zeit.push.product_config +
                    product_config))
