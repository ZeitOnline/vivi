import zope.component
import zope.interface

from zeit.magazin.interfaces import IZMOFolder, IZMOSection
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.link.testing


def create_fixture(repository):
    magazin = zeit.cms.repository.folder.Folder()
    zope.interface.alsoProvides(magazin, IZMOSection)
    zope.interface.alsoProvides(magazin, IZMOFolder)
    repository['magazin'] = magazin


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {},
    patches={'zeit.cms': {'zmo-preview-prefix': 'http://localhost/zmo-preview-prefix'}},
    bases=zeit.content.link.testing.CONFIG_LAYER,
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(CONFIG_LAYER)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER, create_fixture)
WSGI_LAYER = zeit.cms.testing.WSGILayer(ZOPE_LAYER)


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER
