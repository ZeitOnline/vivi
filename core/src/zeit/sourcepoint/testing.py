import zeit.cms.repository.interfaces
import zeit.cms.testing


def create_fixture(repository):
    repository['sourcepoint'] = zeit.cms.repository.folder.Folder()
    repository['addefend'] = zeit.cms.repository.folder.Folder()


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'addefend-url': 'http://example.com',
        'addefend-javascript-folder': 'http://xml.zeit.de/addefend/',
        'addefend-filename': 'adf',
        'kilkaya-teaser-splittests-url': 'http://example.com',
        'kilkaya-teaser-splittests-javascript-folder': 'http://xml.zeit.de/kilkaya/',
        'kilkaya-teaser-splittests-filename': 'kil',
    },
    bases=(zeit.cms.testing.CONFIG_LAYER,),
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(CONFIG_LAYER, 'testing.zcml')
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER, create_fixture)
