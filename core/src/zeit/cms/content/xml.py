# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import StringIO

import persistent
import gocept.lxml.objectify

import zope.interface

import zope.app.container.contained

import zeit.cms.content.interfaces
import zeit.cms.content.property


class XMLRepresentationBase(object):

    zope.interface.implements(zeit.cms.content.interfaces.IXMLRepresentation)

    default_template = None  # Define in subclasses

    def __init__(self, xml_source=None):
        if xml_source is None:
            if self.default_template is None:
                raise NotImplementedError(
                    "default_template needs to be set in subclasses")
            xml_source = StringIO.StringIO(self.default_template)
        self.xml = gocept.lxml.objectify.fromfile(xml_source)


class XMLContentBase(XMLRepresentationBase,
                     persistent.Persistent,
                     zope.app.container.contained.Contained):
    """Base class for xml content."""

    zope.interface.implements(zeit.cms.content.interfaces.IXMLContent)

    uniqueId = None
    __name__ = None


@zope.component.adapter(
    zeit.cms.content.interfaces.IDAVPropertiesInXML,
    zeit.cms.content.interfaces.IDAVPropertyChangedEvent)
def map_dav_property_to_xml(context, event):
    content = zeit.cms.content.interfaces.IXMLRepresentation(context)
    attribute = zeit.cms.content.property.AttributeProperty(
        event.property_namespace, event.property_name)
    if event.new_value is zeit.connector.interfaces.DeleteProperty:
        attribute.__delete__(content)
    else:
        attribute.__set__(content, event.new_value)
