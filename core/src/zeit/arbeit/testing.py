import plone.testing
import zeit.cms.testing
import zeit.cms.repository.interfaces
import zeit.content.article.testing
import zeit.content.cp.testing
import zope.component

product_config = """\
<product-config zeit.arbeit>
</product-config>
"""


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml', product_config=(
        product_config +
        zeit.cms.testing.cms_product_config +
        zeit.content.article.testing.product_config +
        zeit.content.cp.testing.product_config
    ))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZCML_LAYER


class Layer(plone.testing.Layer):

    defaultBases = (ZCML_LAYER,)

    def testSetUp(self):
        with zeit.cms.testing.site(self['functional_setup'].getRootFolder()):
            repository = zope.component.getUtility(
                zeit.cms.repository.interfaces.IRepository)
            repository['arbeit'] = zeit.cms.repository.folder.Folder()

LAYER = Layer()
