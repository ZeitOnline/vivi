from zeit.cms.repository.unknown import PersistentUnknownResource
from zeit.content.dynamicfolder.folder import RepositoryDynamicFolder
import plone.testing
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zope.component


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml', product_config=zeit.cms.testing.cms_product_config)


class DynamicLayer(plone.testing.Layer):

    defaultBases = (ZCML_LAYER,)

    def testSetUp(self):
        with zeit.cms.testing.site(self['functional_setup'].getRootFolder()):
            repository = zope.component.getUtility(
                zeit.cms.repository.interfaces.IRepository)

            folder = zeit.cms.repository.folder.Folder()
            repository['data'] = folder
            folder['config.xml'] = PersistentUnknownResource(data=u"""
            <config  xmlns:xi="http://www.w3.org/2001/XInclude">
                <body>
                    <xi:include href="http://xml.zeit.de/data/children.xml"/>
                </body>
            </config>
            """)
            folder['children.xml'] = PersistentUnknownResource(data=u"""\
<?xml version="1.0" encoding="ISO-8859-1"?>
            <weighted-tags>
                <letter id="x" Location_count="2">
                    <tag url_value="xanten" lexical_value="Xanten" />
                    <tag url_value="xinjiang" lexical_value="Xinjiang" />
                </letter>
            </weighted-tags>
            """)

            dynamic = RepositoryDynamicFolder()
            dynamic.config_file = folder['config.xml']
            repository['dynamicfolder'] = dynamic


DYNAMIC_LAYER = DynamicLayer()


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = DYNAMIC_LAYER
