import plone.testing
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zope.component


product_config = """\
<product-config zeit.sourcepoint>
  api-token mytoken
  url http://example.com
  javascript-folder http://xml.zeit.de/sourcepoint/
</product-config>
"""

ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'testing.zcml', product_config=product_config +
    zeit.cms.testing.cms_product_config)


class Layer(plone.testing.Layer):

    defaultBases = (ZCML_LAYER,)

    def testSetUp(self):
        with zeit.cms.testing.site(self['functional_setup'].getRootFolder()):
            repository = zope.component.getUtility(
                zeit.cms.repository.interfaces.IRepository)
            repository['sourcepoint'] = zeit.cms.repository.folder.Folder()

LAYER = Layer()
