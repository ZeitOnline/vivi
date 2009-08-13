# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.interfaces
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.content.gallery.interfaces
import zope.component
import zope.interface


class GalleryReference(object):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(
        zeit.content.gallery.interfaces.IGalleryReference)

    gallery = zeit.cms.content.dav.DAVProperty(
        zeit.content.gallery.interfaces.IGalleryReference['gallery'],
        'http://namespaces.zeit.de/CMS/document', 'artbox_gallery')
    embedded_gallery = zeit.cms.content.dav.DAVProperty(
        zeit.content.gallery.interfaces.IGalleryReference['embedded_gallery'],
        'http://namespaces.zeit.de/CMS/document', 'biga-src')

    def __init__(self, context):
        self.context = context


@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
@zope.component.adapter(GalleryReference)
def gallery_reference_to_webdav_properties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context)



@zope.component.adapter(
    zeit.content.gallery.interfaces.IGalleryReference,
    zeit.content.gallery.interfaces.GallerySource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def gallery_reference_browse_location(context, source):
    """Gallery browse location."""
    return zope.component.queryMultiAdapter(
        (context.context, source),
        zeit.cms.browser.interfaces.IDefaultBrowsingLocation)

