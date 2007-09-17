# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import lxml.etree
import gocept.lxml.objectify

import persistent

import zope.component
import zope.interface

import zope.app.container.contained

import zeit.cms.connector
import zeit.cms.interfaces
import zeit.cms.content.metadata
import zeit.cms.content.util
import zeit.content.centerpage.interfaces


CP_TEMPLATE = """\
<centerpage>
    <head/>
    <body/>
</centerpage>"""


class CenterPage(persistent.Persistent, zope.app.container.contained.Contained,
                 zeit.cms.content.metadata.CommonMetadata):
    """CenterPage"""

    zope.interface.implements(zeit.content.centerpage.interfaces.ICenterPage)

    keywords = ()

    def __init__(self, xml_source=None, __name__=None,
                 **data):
        apply_defaults = False
        if xml_source is None:
            apply_defaults = True
            self.xml = gocept.lxml.objectify.fromstring(CP_TEMPLATE)
        else:
            self.xml = gocept.lxml.objectify.fromfile(xml_source)
        self.uniqueId = None
        self.__name__ = __name__
        if apply_defaults:
            zeit.cms.content.util.applySchemaData(
                self,
                zeit.content.centerpage.interfaces.ICenterPageMetadata,
                data)

    @property
    def xml_source(self):
        return lxml.etree.tostring(self.xml, 'UTF-8', xml_declaration=True)



@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
@zope.component.adapter(zeit.cms.interfaces.IResource)
def centerpageFactory(context):
    cp = CenterPage(xml_source=context.data)
    zeit.cms.interfaces.IWebDAVProperties(cp).update(context.properties)
    return cp


resourceFactory = zeit.cms.connector.xmlContentToResourceAdapterFactory(
    'centerpage')
resourceFactory = zope.component.adapter(
    zeit.content.centerpage.interfaces.ICenterPage)(resourceFactory)


@zope.component.adapter(
    zeit.content.centerpage.interfaces.ICenterPage,
    zeit.cms.content.interfaces.IDAVPropertyChangedEvent)
def mapPropertyToAttribute(cp, event):
    attribute = zeit.cms.content.property.AttributeProperty(
        event.property_namespace, event.property_name)
    attribute.__set__(cp, event.new_value)
