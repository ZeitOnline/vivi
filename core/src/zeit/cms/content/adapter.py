# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import StringIO

import lxml.etree
import lxml.objectify
import xml.sax.saxutils

import zope.annotation
import zope.component
import zope.interface
import zope.security.proxy

import zeit.cms.content.interfaces
import zeit.connector.interfaces
import zeit.connector.resource


@zope.annotation.factory
@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def webDAVPropertiesFactory():
    return zeit.connector.resource.WebDAVProperties()


def xmlContentToResourceAdapterFactory(typ):
    """Adapt content type to IResource"""

    @zope.interface.implementer(zeit.connector.interfaces.IResource)
    def adapter(context):
        xml_source = zeit.cms.content.interfaces.IXMLSource(context)
        try:
            properties = zeit.connector.interfaces.IWebDAVReadProperties(
                context)
        except TypeError:
            properties = zeit.connector.resource.WebDAVProperties()
        return zeit.connector.resource.Resource(
            context.uniqueId, context.__name__, typ,
            data=StringIO.StringIO(xml_source),
            contentType='text/xml',
            properties=properties)

    return adapter


def xmlContentFactory(factory):

    @zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
    @zope.component.adapter(zeit.cms.interfaces.IResource)
    def adapter(context):
        obj = factory(xml_source=context.data)
        zeit.cms.interfaces.IWebDAVWriteProperties(obj).update(
            context.properties)
        return obj

    return adapter

@zope.interface.implementer(zeit.cms.content.interfaces.IXMLSource)
@zope.component.adapter(zeit.cms.content.interfaces.IXMLRepresentation)
def xml_source(context):
    # remove proxy so lxml can serialize
    xml = zope.security.proxy.removeSecurityProxy(context.xml)
    return lxml.etree.tostring(
        xml.getroottree(), encoding='UTF-8', xml_declaration=True)
