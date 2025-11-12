import zope.component

from zeit.wochenende.interfaces import IZWEFolder, IZWESection
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.article.testing


def create_fixture(repository):
    wochenende = zeit.cms.repository.folder.Folder()
    zope.interface.alsoProvides(wochenende, IZWESection)
    zope.interface.alsoProvides(wochenende, IZWEFolder)
    repository['wochenende'] = wochenende


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    zeit.content.article.testing.CONFIG_LAYER, features=['zeit.connector.sql.zope']
)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER, create_fixture)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER
