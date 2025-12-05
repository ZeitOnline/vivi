import zope.component

from zeit.zett.interfaces import IZTTFolder, IZTTSection
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.article.testing


def create_fixture(repository):
    zett = zeit.cms.repository.folder.Folder()
    zope.interface.alsoProvides(zett, IZTTSection)
    zope.interface.alsoProvides(zett, IZTTFolder)
    repository['zett'] = zett


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(zeit.content.article.testing.CONFIG_LAYER)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER, create_fixture)
WSGI_LAYER = zeit.cms.testing.WSGILayer(ZOPE_LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER
