import plone.testing
import zeit.cms.repository.interfaces
import zeit.cms.section.interfaces
import zeit.cms.testcontenttype.interfaces
import zeit.cms.testing
import zope.component
import zope.interface


ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting.zcml', bases=(zeit.cms.testing.CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))


class SectionLayer(plone.testing.Layer):
    defaultBases = (ZOPE_LAYER,)

    def testSetUp(self):
        with zeit.cms.testing.site(self['zodbApp']):
            repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
            example = zeit.cms.repository.folder.Folder()
            zope.interface.alsoProvides(example, IExampleSection)
            repository['example'] = example


SECTION_LAYER = SectionLayer()


class IExampleSection(zeit.cms.section.interfaces.ISection):
    pass


class IExampleContent(zeit.cms.interfaces.ICMSContent, zeit.cms.section.interfaces.ISectionMarker):
    pass


class IExampleTestcontent(
    zeit.cms.testcontenttype.interfaces.IExampleContentType,
    zeit.cms.section.interfaces.ISectionMarker,
):
    pass
