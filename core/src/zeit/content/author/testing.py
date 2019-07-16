import pkg_resources
import zeit.cms.testing
import zeit.find.testing
import zeit.workflow.testing
import zope.testing.doctest

product_config = """
<product-config zeit.content.author>
  author-folder /foo/bar/authors
  biography-questions file://{fixtures}/tests/biography-questions.xml
  sso-api-url http://meine.fake/api/1
  sso-user vivi@zeit.de
  sso-password password
</product-config>
""".format(fixtures=pkg_resources.resource_filename(__name__, '.'))

ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config +
    zeit.workflow.testing.product_config +
    zeit.find.testing.product_config +
    product_config)
WSGI_LAYER = zeit.cms.testing.WSGILayer(name='WSGILayer', bases=(ZCML_LAYER,))


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('layer', ZCML_LAYER)
    kw['package'] = zope.testing.doctest._normalize_module(kw.get('package'))
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):

    layer = WSGI_LAYER
