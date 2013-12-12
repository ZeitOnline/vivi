# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.magazin.interfaces import IZMOSection, IZMOFolder
import gocept.selenium
import gocept.selenium.ztk
import pkg_resources
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.article.testing
import zope.component
import zope.interface


# XXX appending to product config is not very well supported right now
cms_product_config = zeit.cms.testing.cms_product_config.replace(
    '</product-config>', """\
  zmo-preview-prefix http://localhost/zmo-preview-prefix
</product-config>""")

product_config = """\
<product-config zeit.magazin>
  article-template-source file://{base}/tests/article-templates.xml
</product-config>
""".format(base=pkg_resources.resource_filename(__name__, ''))


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml', product_config=(
        product_config
        + cms_product_config
        + zeit.content.article.testing.product_config))


class LAYER(ZCML_LAYER):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        with zeit.cms.testing.site(cls.setup.getRootFolder()):
            repository = zope.component.getUtility(
                zeit.cms.repository.interfaces.IRepository)
            magazin = zeit.cms.repository.folder.Folder()
            zope.interface.alsoProvides(magazin, IZMOSection)
            zope.interface.alsoProvides(magazin, IZMOFolder)
            repository['magazin'] = magazin

    @classmethod
    def testTearDown(cls):
        pass


SELENIUM_LAYER = gocept.selenium.ztk.Layer(LAYER)
