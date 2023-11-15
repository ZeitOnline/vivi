from zeit.magazin.interfaces import IZMOSection, IZMOFolder
import plone.testing
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.article.testing
import zeit.content.link.testing
import zope.component
import zope.interface


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {},
    patches={'zeit.cms': {'zmo-preview-prefix': 'http://localhost/zmo-preview-prefix'}},
    bases=(zeit.content.article.testing.CONFIG_LAYER, zeit.content.link.testing.CONFIG_LAYER),
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
PUSH_LAYER = zeit.push.testing.UrbanairshipTemplateLayer(
    name='UrbanairshipTemplateLayer', bases=(ZOPE_LAYER,)
)


class Layer(plone.testing.Layer):
    defaultBases = (PUSH_LAYER,)

    def testSetUp(self):
        with zeit.cms.testing.site(self['zodbApp']):
            repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
            magazin = zeit.cms.repository.folder.Folder()
            zope.interface.alsoProvides(magazin, IZMOSection)
            zope.interface.alsoProvides(magazin, IZMOFolder)
            repository['magazin'] = magazin


LAYER = Layer()
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(LAYER,))


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER
