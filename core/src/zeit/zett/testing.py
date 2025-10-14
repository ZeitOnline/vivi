import zope.component

from zeit.zett.interfaces import IZTTFolder, IZTTSection
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.article.testing


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    zeit.content.article.testing.CONFIG_LAYER, features=['zeit.connector.sql.zope']
)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)


class Layer(zeit.cms.testing.ContentFixtureLayer):
    defaultBases = (ZOPE_LAYER,)

    def create_fixture(self):
        repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        zett = zeit.cms.repository.folder.Folder()
        zope.interface.alsoProvides(zett, IZTTSection)
        zope.interface.alsoProvides(zett, IZTTFolder)
        repository['zett'] = zett


LAYER = Layer()
WSGI_LAYER = zeit.cms.testing.WSGILayer(LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER
