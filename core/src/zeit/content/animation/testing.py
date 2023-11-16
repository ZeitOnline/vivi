import zeit.cms.testing
import zeit.content.article.testing


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml', bases=(zeit.content.article.testing.CONFIG_LAYER,)
)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))

layer = ZOPE_LAYER


class FunctionalTestCase(zeit.content.article.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER
