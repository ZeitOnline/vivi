import mock
import pkg_resources
import plone.testing
import zeit.cms.testing
import zeit.find.testing
import zope.component


product_config = """
<product-config zeit.content.author>
  author-folder /foo/bar/authors
  biography-questions file://{fixtures}/tests/biography-questions.xml
  roles file://{fixtures}/tests/roles.xml
  sso-api-url http://meine.fake/api/1
  sso-user vivi@zeit.de
  sso-password password
  honorar-url
  honorar-username
  honorar-password
</product-config>
""".format(fixtures=pkg_resources.resource_filename(__name__, '.'))

CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(product_config, bases=(
    zeit.find.testing.CONFIG_LAYER,))


class HonorarMockLayer(plone.testing.Layer):

    def setUp(self):
        self['honorar_mock'] = mock.Mock()
        self['honorar_mock'].search.return_value = []
        self['honorar_mock'].create.return_value = 'mock-honorar-id'
        self.testTearDown()
        self['honorar_orig'] = zope.component.getUtility(
            zeit.content.author.interfaces.IHonorar)
        zope.component.getSiteManager().registerUtility(
            self['honorar_mock'], zeit.content.author.interfaces.IHonorar)

    def tearDown(self):
        zope.component.getSiteManager().registerUtility(
            self['honorar_orig'], zeit.content.author.interfaces.IHonorar)
        del self['honorar_orig']
        del self['honorar_mock']

    def testTearDown(self):
        self['honorar_mock'].search.return_value = []
        self['honorar_mock'].create.return_value = 'mock-honorar-id'
        self['honorar_mock'].reset_mock()


HONORAR_MOCK_LAYER = HonorarMockLayer()

ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER, HONORAR_MOCK_LAYER))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('layer', ZOPE_LAYER)
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):

    layer = WSGI_LAYER
