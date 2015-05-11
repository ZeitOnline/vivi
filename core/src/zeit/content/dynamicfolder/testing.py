# coding: utf-8
from zeit.cms.repository.unknown import PersistentUnknownResource
from zeit.content.dynamicfolder.folder import RepositoryDynamicFolder
import plone.testing
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.cp.testing
import zope.component


ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting.zcml', product_config=(
    zeit.cms.testing.cms_product_config
    + zeit.content.cp.testing.product_config))


class DynamicLayer(plone.testing.Layer):

    defaultBases = (ZCML_LAYER,)

    def testSetUp(self):
        with zeit.cms.testing.site(self['functional_setup'].getRootFolder()):
            repository = zope.component.getUtility(
                zeit.cms.repository.interfaces.IRepository)

            folder = zeit.cms.repository.folder.Folder()
            repository['data'] = folder
            folder['config.xml'] = PersistentUnknownResource(data=u"""
            <config xmlns:xi="http://www.w3.org/2001/XInclude">
              <head>
                <cp_template>http://xml.zeit.de/data/template.xml</cp_template>
              </head>
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
                <tag url_value="xaernten" lexical_value="Xärnten" />
              </letter>
            </weighted-tags>
            """)
            folder['template.xml'] = PersistentUnknownResource(data=u"""
            <centerpage
              xmlns:cp="http://namespaces.zeit.de/CMS/cp"
              type="centerpage">
              <head>
              </head>
              <body>
                 <title>{{lexical_value}}</title>
                 <cluster area="feature" kind="solo" visible="True">
                   <region area="lead" kind="single"
                     count="2" automatic="True" automatic_type="query"
                     visible="True" hide-dupes="True">
                     <container cp:type="auto-teaser" module="buttons"
                        visible="True" cp:__name__="id-1"/>
                     <container cp:type="auto-teaser" module="buttons"
                        visible="True" cp:__name__="id-2"/>
                     <raw_query>
                        published:"published" AND keywords: {{url_value}}
                     </raw_query>
                   </region>
                 </cluster>
               </body>
            </centerpage>""")

            dynamic = RepositoryDynamicFolder()
            dynamic.config_file = folder['config.xml']
            repository['dynamicfolder'] = dynamic


DYNAMIC_LAYER = DynamicLayer()


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = DYNAMIC_LAYER
