# coding: utf-8
from zeit.cms.repository.unknown import PersistentUnknownResource
from zeit.content.dynamicfolder.folder import RepositoryDynamicFolder
import pkg_resources
import plone.testing
import transaction
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.cp.testing
import zeit.workflow.testing
import zope.component


ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting.zcml', product_config=(
    zeit.cms.testing.cms_product_config +
    zeit.workflow.testing.product_config +
    zeit.content.cp.testing.product_config))


class DynamicLayer(plone.testing.Layer):

    defaultBases = (ZCML_LAYER,)

    def testSetUp(self):
        with zeit.cms.testing.site(self['functional_setup'].getRootFolder()):
            repository = zope.component.getUtility(
                zeit.cms.repository.interfaces.IRepository)

            folder = zeit.cms.repository.folder.Folder()
            repository['data'] = folder
            for name in ['config.xml', 'tags.xml', 'template.xml']:
                folder[name] = PersistentUnknownResource(
                    data=pkg_resources.resource_string(
                        __name__, 'tests/fixtures/%s' % name).decode(
                            'latin-1'))

            dynamic = RepositoryDynamicFolder()
            dynamic.config_file = folder['config.xml']
            repository['dynamicfolder'] = dynamic
            transaction.commit()


DYNAMIC_LAYER = DynamicLayer()


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = DYNAMIC_LAYER
