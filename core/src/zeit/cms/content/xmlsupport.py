# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import StringIO

import lxml.objectify

import persistent
import gocept.lxml.objectify

import zope.interface
import zope.security.proxy

import zope.app.container.contained

import zeit.connector.interfaces
import zeit.cms.checkout.interfaces
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

    def __cmp__(self, other):
        if not zeit.cms.interfaces.ICMSContent.providedBy(other):
            return -1
        return cmp(self.__name__, other.__name__)

_default_marker = object()


class PropertyToXMLAttribute(object):
    """Attribute nodes reside in the head."""

    zope.component.adapts(zeit.cms.content.interfaces.IXMLRepresentation)
    zope.interface.implements(
        zeit.cms.content.interfaces.IDAVPropertyXMLSynchroniser)

    path = lxml.objectify.ObjectPath('.head.attribute')

    def __init__(self, context):
        self.context = context
        self.properties = zeit.connector.interfaces.IWebDAVProperties(context)

    def set(self, namespace, name, value=_default_marker):
        self.delAttribute(namespace, name)
        if value is _default_marker:
            value = self.properties[(name, namespace)]
        if value is not zeit.connector.interfaces.DeleteProperty:
            self.addAttribute(namespace, name, value)

    def sync(self):
        # Remove all properties in xml first
        self.path.setattr(self.context.xml, [])

        # Now, set each property to xml, sort them to get a consistent xml
        for ((name, namespace), value) in sorted(self.properties.items()):
            if value is zeit.connector.interfaces.DeleteProperty:
                continue
            self.addAttribute(namespace, name, value)

    def addAttribute(self, namespace, name, value):
        root = self.context.xml
        self.path.addattr(root, value)
        node = self.path.find(root)[-1]
        node.set('ns', namespace)
        node.set('name', name)

    def delAttribute(self, namespace, name):
        root = self.context.xml
        xpath = '//head/attribute[@ns="%s" and @name="%s"]' % (
            namespace, name)
        for node in root.findall(xpath):
            parent = node.getparent()
            parent.remove(node)


@zope.component.adapter(
    zeit.cms.content.interfaces.IDAVPropertiesInXML,
    zeit.cms.content.interfaces.IDAVPropertyChangedEvent)
def map_dav_property_to_xml(context, event):
    """Copy dav properties to XML if possible.

    """
    # Remove security proxy: If the user was allowed to change the property
    # (via setattr) *we* copy that to the xml, regardles of the security.
    content = zope.security.proxy.removeSecurityProxy(
        zeit.cms.content.interfaces.IXMLRepresentation(context))
    sync = zeit.cms.content.interfaces.IDAVPropertyXMLSynchroniser(content)
    sync.set(event.property_namespace, event.property_name, event.new_value)


@zope.component.adapter(
    zeit.cms.content.interfaces.IDAVPropertiesInXML,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def map_dav_properties_to_xml_before_checkin(context, event):
    """Copy over all DAV properties to the xml before checkin.

    """
    content = zope.security.proxy.removeSecurityProxy(
        zeit.cms.content.interfaces.IXMLRepresentation(context))
    sync = zeit.cms.content.interfaces.IDAVPropertyXMLSynchroniser(content)
    sync.sync()
