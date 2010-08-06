# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.interfaces
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.content.gallery.interfaces
import zope.component
import zope.interface


class GalleryReference(zeit.cms.content.dav.DAVPropertiesAdapter):

    zope.interface.implements(
        zeit.content.gallery.interfaces.IGalleryReference)

    gallery = zeit.cms.content.dav.DAVProperty(
        zeit.content.gallery.interfaces.IGalleryReference['gallery'],
        'http://namespaces.zeit.de/CMS/document', 'artbox_gallery')

    def __init__(self, context):
        self.context = self.__parent__ = context


@zope.component.adapter(
    zeit.content.gallery.interfaces.IGalleryReference,
    zeit.content.gallery.interfaces.GallerySource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def gallery_reference_browse_location(context, source):
    """Gallery browse location."""
    return zope.component.queryMultiAdapter(
        (context.__parent__, source),
        zeit.cms.browser.interfaces.IDefaultBrowsingLocation)


class XMLReferenceUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):

    target_iface = zeit.content.gallery.interfaces.IGalleryReference

    def update_with_context(self, node, reference):
        for gallery_node in node.findall('gallery'):
            node.remove(gallery_node)
        if reference.gallery is not None:
            gref = zope.component.getAdapter(
                reference.gallery, zeit.cms.content.interfaces.IXMLReference,
                name='related')
            gref.tag = 'gallery'
            node.append(gref)
