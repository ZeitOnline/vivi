import zope.component

from zeit.wochenende.interfaces import IZWEFolder, IZWESection
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
        wochenende = zeit.cms.repository.folder.Folder()
        zope.interface.alsoProvides(wochenende, IZWESection)
        zope.interface.alsoProvides(wochenende, IZWEFolder)
        repository['wochenende'] = wochenende


LAYER = Layer()


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = LAYER
