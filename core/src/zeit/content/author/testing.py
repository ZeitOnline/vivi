import pkg_resources
import zeit.cms.testing
import zeit.find.testing
import zeit.workflow.testing


product_config = """
<product-config zeit.content.author>
  author-folder /foo/bar/authors
  biography-questions file://{fixtures}/tests/biography-questions.xml
  sso-api-url http://meine.fake/api/1
  sso-user vivi@zeit.de
  sso-password password
</product-config>
""".format(fixtures=pkg_resources.resource_filename(__name__, '.'))

CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(product_config, bases=(
    zeit.workflow.testing.CONFIG_LAYER,
    zeit.find.testing.CONFIG_LAYER))
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('layer', ZOPE_LAYER)
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = WSGI_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):

    layer = WSGI_LAYER
