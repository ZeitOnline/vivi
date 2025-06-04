import plone.testing
import zope.component

import zeit.cms.repository.interfaces
import zeit.cms.testing


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'teaser_splittests-url': 'http://example.com',
        'teaser_splittests-json-folder': 'http://xml.zeit.de/kilkaya-teaser-splittests/',
        'teaser_splittests-filename': 'splittests',
    },
    bases=(zeit.cms.testing.CONFIG_LAYER,),
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer('testing.zcml', bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))


class Layer(plone.testing.Layer):
    defaultBases = (ZOPE_LAYER,)

    def testSetUp(self):
        with zeit.cms.testing.site(self['zodbApp']):
            repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
            repository['kilkaya-teaser-splittests'] = zeit.cms.repository.folder.Folder()


LAYER = Layer()
