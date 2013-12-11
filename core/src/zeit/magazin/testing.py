# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.magazin.interfaces import IZMOSection
import pkg_resources
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zope.component
import zope.interface


product_config = zeit.cms.testing.cms_product_config.replace(
    '</product-config>', """\
  zmo-preview-prefix http://localhost/zmo-preview-prefix
    article-template-source file://{base}/tests/article-templates.xml
</product-config>""".format(
    base=pkg_resources.resource_filename(__name__, '')))


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml', product_config=product_config)


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
            repository['magazin'] = magazin

    @classmethod
    def testTearDown(cls):
        pass
