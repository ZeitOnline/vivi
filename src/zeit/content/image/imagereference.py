# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component as grok
import zeit.cms.checkout.interfaces
import zeit.cms.content.reference
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

    _images = zeit.cms.content.reference.MultiResource(
        '.head.image', 'image')

    @property
    def image(self):
        if not self._images:
            return
        return self._images[0]

    @image.setter
    def image(self, value):
        if value is None:
            value = ()
        else:
            value = (value, )
        self._images = value


class ImageReference(zeit.cms.content.reference.Reference):

    grok.name('image')

    @property
    def target_unique_id(self):
        unique_id = self.xml.get('base-id')
        if unique_id is None:
            unique_id = self.xml.get('src')
        return unique_id


@zope.component.adapter(zeit.cms.content.interfaces.ITemplate)
@zope.interface.implementer(zeit.content.image.interfaces.IImages)
def images_from_template(context):
    return ImagesAdapter(context)


class XMLReferenceUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):
    """Add the *first* referenced image to the feed entry."""

    target_iface = zeit.content.image.interfaces.IImages

    def update_with_context(self, entry, images):
        if images.image is not None:
            # only add first image
            image = images.image
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
    ImagesAdapter._images.update_metadata(images)


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.relation.interfaces.IReferenceProvider)
def image_references(context):
    images = zeit.content.image.interfaces.IImages(context, None)
    if images is None:
        return
    image = images.image
    if image is None:
        return ()
    return (image, )


class References(object):

    zope.interface.implements(zeit.content.image.interfaces.IReferences)
    zope.component.adapts(zeit.content.image.interfaces.IImageGroup)

    def __init__(self, context):
        self.context = context

    @property
    def references(self):
        relations = zope.component.getUtility(
            zeit.cms.relation.interfaces.IRelations)
        relating_objects = relations.get_relations(self.context)
        return tuple(relating_objects)
