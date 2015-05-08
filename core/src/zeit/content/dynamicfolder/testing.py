from zeit.cms.repository.unknown import PersistentUnknownResource
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.dynamicfolder.folder
import zope.component


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml', product_config=zeit.cms.testing.cms_product_config)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZCML_LAYER

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        self.repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    def create_xml_config(self):
        folder = zeit.cms.repository.folder.Folder()
        self.repository['data'] = folder
        folder['config.xml'] = PersistentUnknownResource(data=u"""
            <config  xmlns:xi="http://www.w3.org/2001/XInclude">
                <body>
                    <xi:include href="http://xml.zeit.de/data/children.xml"/>
                </body>
            </config>
        """)
        folder['children.xml'] = PersistentUnknownResource(data=u"""
            <weighted-tags>
                <letter id="x" Location_count="2">
                    <tag url_value="xanten" lexical_value="Xanten" />
                    <tag url_value="xinjiang" lexical_value="Xinjiang" />
                </letter>
            </weighted-tags>
        """)

    def create_dynamic_folder(self):
        folder = zeit.content.dynamicfolder.folder.RepositoryDynamicFolder()
        folder.config_file_id = 'http://xml.zeit.de/data/config.xml'
        self.repository['dynamicfolder'] = folder
        return folder
