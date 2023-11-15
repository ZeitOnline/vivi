import plone.testing
import zeit.cms.testing
import zeit.cms.repository.interfaces
import zeit.content.article.testing
import zope.component


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(zeit.content.article.testing.CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))


class Layer(plone.testing.Layer):
    defaultBases = (ZOPE_LAYER,)

    def testSetUp(self):
        with zeit.cms.testing.site(self['zodbApp']):
            repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
            repository['arbeit'] = zeit.cms.repository.folder.Folder()


LAYER = Layer()
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER
