import plone.testing
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zope.component


product_config = """\
<product-config zeit.sourcepoint>
  sp-api-token mytoken
  sp-url http://example.com
  sp-javascript-folder http://xml.zeit.de/sourcepoint/
  addefend-api-token mytoken
  addefend-url http://example.com
  addefend-javascript-folder http://xml.zeit.de/addefend/
</product-config>
"""

CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(product_config, bases=(
    zeit.cms.testing.CONFIG_LAYER,))
ZCML_LAYER = zeit.cms.testing.ZCMLLayer('testing.zcml', bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))


class Layer(plone.testing.Layer):

    defaultBases = (ZOPE_LAYER,)

    def testSetUp(self):
        with zeit.cms.testing.site(self['zodbApp']):
            repository = zope.component.getUtility(
                zeit.cms.repository.interfaces.IRepository)
            repository['sourcepoint'] = zeit.cms.repository.folder.Folder()
            repository['addefend'] = zeit.cms.repository.folder.Folder()


LAYER = Layer()
