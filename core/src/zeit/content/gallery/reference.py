# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.cms.content.dav
import zeit.content.gallery.interfaces


class GalleryReference(object):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(
        zeit.content.gallery.interfaces.IGalleryReference)

    gallery = zeit.cms.content.dav.DAVProperty(
        zeit.content.gallery.interfaces.IGalleryReference['gallery'],
        'http://namespaces.zeit.de/CMS/document', 'artbox_gallery')

    def __init__(self, context):
        self.context = context


@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
@zope.component.adapter(GalleryReference)
def gallery_reference_to_webdav_properties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context)
