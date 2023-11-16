from unittest import mock
import importlib.resources
import plone.testing
import zeit.cms.testing
import zeit.find.testing
import zope.component


product_config = """
<product-config zeit.content.author>
  author-folder /foo/bar/authors
  biography-questions file://{here}/tests/biography-questions.xml
  roles file://{here}/tests/roles.xml
  sso-api-url http://meine.fake/api/1
  sso-user vivi@zeit.de
  sso-password password
</product-config>
""".format(here=importlib.resources.files(__package__))

CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    product_config, bases=(zeit.find.testing.CONFIG_LAYER,)
)


class HonorarMockLayer(plone.testing.Layer):
    def testTearDown(self):
        honorar = zope.component.getUtility(zeit.content.author.interfaces.IHonorar)
        if isinstance(honorar, mock.Mock):
            honorar.search.return_value = []
            honorar.create.return_value = 'mock-honorar-id'
            honorar.reset_mock()


HONORAR_MOCK_LAYER = HonorarMockLayer()

ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(
    bases=(ZCML_LAYER, zeit.find.testing.SEARCH_MOCK_LAYER, HONORAR_MOCK_LAYER)
)
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('layer', ZOPE_LAYER)
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER
