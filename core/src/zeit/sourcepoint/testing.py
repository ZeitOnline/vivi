import zope.component

import zeit.cms.repository.interfaces
import zeit.cms.testing


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
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    config_file='testing.zcml', bases=CONFIG_LAYER, features=['zeit.connector.sql.zope']
)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)


class Layer(zeit.cms.testing.Layer):
    defaultBases = (ZOPE_LAYER,)

    def testSetUp(self):
        with zeit.cms.testing.site(self['zodbApp']):
            repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
            repository['sourcepoint'] = zeit.cms.repository.folder.Folder()
            repository['addefend'] = zeit.cms.repository.folder.Folder()


LAYER = Layer()
