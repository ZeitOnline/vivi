# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import StringIO
import logging

import lxml.etree
import lxml.objectify

import zope.annotation
import zope.component
import zope.interface
import zope.location.location
import zope.security.proxy

import zope.app.container.interfaces

import zeit.connector.interfaces
import zeit.connector.resource

import zeit.cms.interfaces
import zeit.cms.content.interfaces
import zeit.cms.repository.interfaces


logger = logging.getLogger(__name__)


@zope.annotation.factory
@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def webDAVPropertiesFactory():
    return zeit.connector.resource.WebDAVProperties()


@zope.component.adapter(zeit.connector.interfaces.IWebDAVProperties)
@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
def webdavproperties_to_cms_content(context):
    if not zope.location.interfaces.ILocation.providedBy(context):
        return
    return zeit.cms.interfaces.ICMSContent(context.__parent__, None)


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
        try:
            return factory(xml_source=context.data)
        except lxml.etree.XMLSyntaxError, e:
            logger.warning("Could not parse XML of %s: %s (%s)" % (
                context.id, e.__class__.__name__, e))
            return None

    return adapter


@zope.interface.implementer(zeit.cms.content.interfaces.IXMLSource)
@zope.component.adapter(zeit.cms.content.interfaces.IXMLRepresentation)
def xml_source(context):
    """Serialize an xml tree."""
    # Remove proxy so lxml can serialize
    xml = zope.security.proxy.removeSecurityProxy(context.xml)
    return lxml.etree.tostring(
        xml.getroottree(), encoding='UTF-8', xml_declaration=True,
        pretty_print=True)


@zope.interface.implementer(zeit.cms.content.interfaces.IContentSortKey)
@zope.component.adapter(zope.app.container.interfaces.IContained)
def content_sort_key(context):
    weight = 0
    key = context.__name__.lower()
    return (weight, key)
