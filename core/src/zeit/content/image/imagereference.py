# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.async
import lxml.etree
import lxml.objectify
import rwproperty
import zeit.cms.checkout.helper
import zeit.cms.checkout.interfaces
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.related.related
import zeit.cms.relation.interfaces
import zeit.content.image.interfaces
import zope.component
import zope.interface


class ImagesAdapter(zeit.cms.related.related.RelatedBase):

    zope.component.adapts(zeit.cms.content.interfaces.IXMLContent)
    zope.interface.implements(zeit.content.image.interfaces.IImages)

    path = lxml.objectify.ObjectPath('.head.image')
    xml_reference_name = 'image'

    @rwproperty.getproperty
    def images(self):
        return self._get_related()

    @rwproperty.setproperty
    def images(self, value):
        self._set_related(value)

    def _get_unique_id(self, element):
        unique_id = element.get('base-id')
        if unique_id is None:
            unique_id = element.get('src')
        return unique_id


@zope.component.adapter(zeit.cms.content.interfaces.ITemplate)
@zope.interface.implementer(zeit.content.image.interfaces.IImages)
def images_from_template(context):
    return ImagesAdapter(context)


class XMLReferenceUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):
    """Add the *first* referenced image to the feed entry."""

    target_iface = zeit.content.image.interfaces.IImages

    def update_with_context(self, entry, images):
        if images.images:
            # only add first image
            image = images.images[0]
            image_node = zope.component.queryAdapter(
                image, zeit.cms.content.interfaces.IXMLReference, name='image')
            if image_node is None:
                raise ValueError(
                    ("Could not create xml reference 'image' for %s which "
                     "is referenced in %s.") % (
                         image.uniqueId, self.context.uniqueId))
            entry['image'] = image_node
        else:
            # No image referenced. Remove an image node we might have produced
            # earlier.
            image_node = entry.find('image')
            if image_node is not None:
                entry.remove(image_node)


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_image_reference_on_checkin(context, event):
    __traceback_info__ = (context.uniqueId,)
    images = zeit.content.image.interfaces.IImages(context, None)
    if images is None:
        return
    image_list = images.images
    if image_list:
        images.images = image_list


def image_referenced_by(content, catalog):
    """Index support for relation catalog."""
    images = zeit.content.image.interfaces.IImages(content, None)
    if images is None:
        return
    return images.images


def update_image_reference_of_checked_out(checked_out):
    """Update the object which relate the checked out.

    returns True if object has changed, False otherwise.

    """
    images = zeit.content.image.interfaces.IImages(checked_out, None)
    if images is None:
        return False
    xml_before = lxml.etree.tostring(
        zeit.cms.content.interfaces.IXMLRepresentation(images).xml)

    # Update related
    images.images = images.images

    # Make sure there actually was a change.
    xml_after = lxml.etree.tostring(
        zeit.cms.content.interfaces.IXMLRepresentation(images).xml)

    if xml_before == xml_after:
        return False

    return True


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def update_objects_referenced_by_images_handler(context, event):
    update_objects_referenced_by_images(context)


@gocept.async.function(service='events')
def update_objects_referenced_by_images(context):
    """Update objects which are referenced by images."""
    relations = zope.component.getUtility(
        zeit.cms.relation.interfaces.IRelations)
    relating_objects = relations.get_relations(context, 'image_referenced_by')
    for related_object in relating_objects:
        zeit.cms.checkout.helper.with_checked_out(
            related_object, update_image_reference_of_checked_out)


class References(object):

    zope.interface.implements(zeit.content.image.interfaces.IReferences)
    zope.component.adapts(zeit.content.image.interfaces.IImageGroup)

    def __init__(self, context):
        self.context = context

    @property
    def references(self):
        relations = zope.component.getUtility(
            zeit.cms.relation.interfaces.IRelations)
        relating_objects = relations.get_relations(self.context,
                                                   'image_referenced_by')
        return tuple(relating_objects)
