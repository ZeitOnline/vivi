# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import StringIO

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
import zeit.content.gallery.interfaces


# A gallery used to be a center page, that's why we initialize it with such a
# template.
GALLERY_TEMPLATE = """\
<centerpage>
    <head/>
    <body/>
</centerpage>"""



class Gallery(persistent.Persistent,
              zope.app.container.contained.Contained,
              zeit.cms.content.metadata.CommonMetadata):
    """CenterPage"""

    zope.interface.implements(zeit.content.gallery.interfaces.IGallery)

    image_folder = zeit.cms.content.property.SingleResourceProperty(
        '.head.image-folder')

    uniqueId = None
    __name__ = None

    def __init__(self, xml_source=None):
        if xml_source is None:
            xml_source = StringIO.StringIO(GALLERY_TEMPLATE)
        self.xml = gocept.lxml.objectify.fromfile(xml_source)

    @property
    def xml_source(self):
        return lxml.etree.tostring(self.xml, 'UTF-8', xml_declaration=True)



@zope.interface.implementer(zeit.content.gallery.interfaces.IGallery)
@zope.component.adapter(zeit.cms.interfaces.IResource)
def galleryFactory(context):
    obj = Gallery(xml_source=context.data)
    zeit.cms.interfaces.IWebDAVProperties(obj).update(context.properties)
    return obj


resourceFactory = zeit.cms.connector.xmlContentToResourceAdapterFactory(
    'image-gallery')
resourceFactory = zope.component.adapter(
    zeit.content.gallery.interfaces.IGallery)(resourceFactory)


@zope.component.adapter(
    zeit.content.gallery.interfaces.IGallery,
    zeit.cms.content.interfaces.IDAVPropertyChangedEvent)
def mapPropertyToAttribute(cp, event):
    attribute = zeit.cms.content.property.AttributeProperty(
        event.property_namespace, event.property_name)
    attribute.__set__(cp, event.new_value)
