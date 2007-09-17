# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import StringIO

import lxml.etree
import lxml.objectify
import xml.sax.saxutils

import zope.annotation
import zope.component
import zope.interface

import zeit.cms.content.interfaces
import zeit.connector.interfaces
import zeit.connector.resource


class BaseTeaserXMLRepresentation(object):

    zope.interface.implements(zeit.cms.content.interfaces.IXMLRepresentation)

    tag_name = None

    def __init__(self, context):
        self.context = context

    @property
    def xml(self):
        title = self.context.title or u''
        text = self.context.text or u''
        xml_str = (u'<%s xmlns="%s"><title>%s</title>'
                   u'<text>%s</text></%s>') % (
            self.tag_name,
            zeit.cms.interfaces.TEASER_NAMESPACE,
            xml.sax.saxutils.escape(title),
            xml.sax.saxutils.escape(text),
            self.tag_name)
        return lxml.objectify.fromstring(xml_str)

    @property
    def xml_source(self):
        return lxml.etree.tostring(self.xml, pretty_print=True)


class TeaserXMLRepresentation(BaseTeaserXMLRepresentation):

    zope.component.adapts(zeit.cms.content.interfaces.ITeaser)
    tag_name = 'teaser'


class IndexTeaserXMLRepresentation(BaseTeaserXMLRepresentation):

    zope.component.adapts(zeit.cms.content.interfaces.IIndexTeaser)
    tag_name = 'indexteaser'


@zope.annotation.factory
@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def webDAVPropertiesFactory():
    return zeit.connector.resource.WebDAVProperties()


def xmlContentToResourceAdapterFactory(typ):
    """Adapt content type to IResource"""

    @zope.interface.implementer(zeit.connector.interfaces.IResource)
    def adapter(context):
        try:
            properties = zeit.connector.interfaces.IWebDAVReadProperties(context)
        except TypeError:
            properties = zeit.connector.resource.WebDAVProperties()
        return zeit.connector.resource.Resource(
            context.uniqueId, context.__name__, typ,
            data=StringIO.StringIO(context.xml_source),
            contentType='text/xml',
            properties=properties)

    return adapter


