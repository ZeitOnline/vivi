from unittest import mock
import importlib.resources

import zope.component

import zeit.cms.testing
import zeit.find.testing


HERE = importlib.resources.files(__package__)
CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'author-folder': '/foo/bar/authors',
        'biography-questions': f'file://{HERE}/tests/biography-questions.xml',
        'roles': f'file://{HERE}/tests/roles.xml',
        'sso-api-url': 'http://meine.fake/api/1',
        'sso-user': 'vivi@zeit.de',
        'sso-password': 'password',
    },
    bases=(zeit.find.testing.CONFIG_LAYER,),
)


class HonorarMockLayer(zeit.cms.testing.Layer):
    def testTearDown(self):
        honorar = zope.component.getUtility(zeit.content.author.interfaces.IHonorar)
        if isinstance(honorar, mock.Mock):
            honorar.search.return_value = []
            honorar.create.return_value = 9876
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
