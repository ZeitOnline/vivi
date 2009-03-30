# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import lxml.etree
import pkg_resources
import zeit.cms.content.adapter
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zeit.cms.interfaces
import zeit.content.cp.interfaces
import zope.interface


class CenterPage(zeit.cms.content.metadata.CommonMetadata):
    """XXX docme"""

    zope.interface.implements(zeit.content.cp.interfaces.ICenterPage)

    default_template = pkg_resources.resource_string(__name__,
                                                     'cp-template.xml')
    editable_areas = {
        'lead': lxml.etree.XPath('region[@area="lead"]'),
        'informatives': lxml.etree.XPath('region[@area="informatives"]'),
        'mosaic': lxml.etree.XPath('cluster[@area="teaser-mosaic"]'),
    }


    def __getitem__(self, key):
        xml = self.editable_areas[key](self.xml['body'])[0]
        area = zope.component.getMultiAdapter(
            (self, xml),
            zeit.content.cp.interfaces.IEditableArea,
            name=key)
        return area



centerpageFactory = zeit.cms.content.adapter.xmlContentFactory(CenterPage)


resourceFactory = zeit.cms.connector.xmlContentToResourceAdapterFactory(
    'centerpage-2009')
resourceFactory = zope.component.adapter(
    zeit.content.cp.interfaces.ICenterPage)(resourceFactory)
