import zope.component
import zope.interface

import zeit.cms.repository.interfaces
import zeit.cms.section.interfaces
import zeit.cms.testcontenttype.interfaces
import zeit.cms.testing


def create_fixture(repository):
    example = zeit.cms.repository.folder.Folder()
    zope.interface.alsoProvides(example, IExampleSection)
    repository['example'] = example


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(zeit.cms.testing.CONFIG_LAYER)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER, create_fixture)


class IExampleSection(zeit.cms.section.interfaces.ISection):
    pass


class IExampleContent(zeit.cms.interfaces.ICMSContent, zeit.cms.section.interfaces.ISectionMarker):
    pass


class IExampleTestcontent(
    zeit.cms.testcontenttype.interfaces.IExampleContentType,
    zeit.cms.section.interfaces.ISectionMarker,
):
    pass
