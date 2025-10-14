import zope.component
import zope.interface

from zeit.magazin.interfaces import IZMOFolder, IZMOSection
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.article.testing
import zeit.content.link.testing


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {},
    patches={'zeit.cms': {'zmo-preview-prefix': 'http://localhost/zmo-preview-prefix'}},
    bases=(zeit.content.article.testing.CONFIG_LAYER, zeit.content.link.testing.CONFIG_LAYER),
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(CONFIG_LAYER, features=['zeit.connector.sql.zope'])
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)
PUSH_LAYER = zeit.push.testing.UrbanairshipTemplateLayer(ZOPE_LAYER)


class Layer(zeit.cms.testing.ContentFixtureLayer):
    defaultBases = (PUSH_LAYER,)

    def create_fixture(self):
        repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        magazin = zeit.cms.repository.folder.Folder()
        zope.interface.alsoProvides(magazin, IZMOSection)
        zope.interface.alsoProvides(magazin, IZMOFolder)
        repository['magazin'] = magazin


LAYER = Layer()
WSGI_LAYER = zeit.cms.testing.WSGILayer(LAYER)


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER
