from zeit.magazin.interfaces import IZMOSection, IZMOFolder
import gocept.httpserverlayer.wsgi
import gocept.selenium
import pkg_resources
import plone.testing
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.article.testing
import zeit.content.gallery.testing
import zeit.content.link.testing
import zeit.push.testing
import zope.component
import zope.interface


# XXX appending to product config is not very well supported right now
cms_product_config = zeit.cms.testing.cms_product_config.replace(
    '</product-config>', """\
  zmo-preview-prefix http://localhost/zmo-preview-prefix
</product-config>""")

product_config = """\
<product-config zeit.magazin>
</product-config>
""".format(base=pkg_resources.resource_filename(__name__, ''))


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml', product_config=(
        product_config +
        cms_product_config +
        zeit.push.testing.product_config +
        zeit.content.article.testing.product_config +
        zeit.content.gallery.testing.product_config +
        zeit.content.link.testing.product_config))


PUSH_LAYER = zeit.push.testing.UrbanairshipTemplateLayer(
    name='UrbanairshipTemplateLayer', bases=(ZCML_LAYER,))


class Layer(plone.testing.Layer):

    defaultBases = (PUSH_LAYER,)

    def testSetUp(self):
        with zeit.cms.testing.site(self['functional_setup'].getRootFolder()):
            repository = zope.component.getUtility(
                zeit.cms.repository.interfaces.IRepository)
            magazin = zeit.cms.repository.folder.Folder()
            zope.interface.alsoProvides(magazin, IZMOSection)
            zope.interface.alsoProvides(magazin, IZMOFolder)
            repository['magazin'] = magazin

LAYER = Layer()


WSGI_LAYER = zeit.cms.testing.WSGILayer(name='WSGILayer', bases=(LAYER,))
HTTP_LAYER = gocept.httpserverlayer.wsgi.Layer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = gocept.selenium.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
SELENIUM_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))
