import grokcore.component as grok
import zope.component
import zope.interface

import zeit.cms.checkout.interfaces
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.related.related
import zeit.cms.relation.interfaces
import zeit.content.image.interfaces


@zope.component.adapter(zeit.cms.content.interfaces.IXMLContent)
@zope.interface.implementer(zeit.content.image.interfaces.IImages)
class ImagesAdapter(zeit.cms.related.related.RelatedBase):
    image = zeit.cms.content.reference.SingleResource('.head.image', 'image')

    fill_color = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.head.image', 'fill_color', zeit.content.image.interfaces.IImages['fill_color']
    )


@grok.implementer(zeit.content.image.interfaces.IImageReference)
class ImageReference(zeit.cms.content.reference.Reference):
    grok.name('image')
    grok.provides(zeit.cms.content.interfaces.IReference)

    # XXX The *_original XML paths must be kept in sync with
    # z.c.image.metadata.XMLReferenceUpdater

    _title_local = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'title_local', zeit.content.image.interfaces.IImageReference['title']
    )

    _alt_local = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'alt_local', zeit.content.image.interfaces.IImageReference['alt']
    )

    _caption_local = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'caption_local', zeit.content.image.interfaces.IImageReference['caption']
    )

    def __getattribute__(self, key):
        if key in zope.schema.getFieldNames(zeit.content.image.interfaces.IImageMetadata):
            field = zeit.content.image.interfaces.IImageMetadata[key]
            try:
                value = object.__getattribute__(self, '_%s_local' % key)
            except AttributeError:
                value = field.missing_value
            if value == field.missing_value:
                target_metadata = zeit.content.image.interfaces.IImageMetadata(self.target, None)
                value = getattr(target_metadata, key, value)
            return value
        else:
            return object.__getattribute__(self, key)

    def __setattr__(self, key, value):
        __traceback_info__ = (key, value)
        if key in zope.schema.getFieldNames(
            zeit.content.image.interfaces.IImageMetadata
        ) and hasattr(self, '_%s_local' % key):
            key = '_%s_local' % key
        super().__setattr__(key, value)

    @property
    def target_unique_id(self):
        unique_id = self.xml.get('base-id')
        if unique_id is None:
            unique_id = self.xml.get('src')
        return unique_id

    def _update_target_unique_id(self):
        if self.xml.get('base-id'):
            self.xml.set('base-id', self.target.uniqueId)
        elif self.xml.get('src'):
            self.xml.set('src', self.target.uniqueId)

    def update_metadata(self, suppress_errors=False):
        super().update_metadata(suppress_errors)
        for name in zope.schema.getFieldNames(zeit.content.image.interfaces.IImageMetadata):
            if hasattr(self, name):
                value = getattr(self, name, None)
                if value is not None:
                    setattr(self, name, value)


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
                image, zeit.cms.content.interfaces.IXMLReference, name='image'
            )
            if image_node is None:
                if not self.suppress_errors:
                    raise ValueError(
                        (
                            "Could not create xml reference 'image' for %s which "
                            'is referenced in %s.'
                        )
                        % (image.uniqueId, self.context.uniqueId)
                    )
            else:
                entry['image'] = image_node
        else:
            # No image referenced. Remove an image node we might have produced
            # earlier.
            image_node = entry.find('image')
            if image_node is not None:
                entry.remove(image_node)


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent, zeit.cms.checkout.interfaces.IBeforeCheckinEvent
)
def update_image_reference_on_checkin(context, event):
    __traceback_info__ = (context.uniqueId,)
    images = zeit.content.image.interfaces.IImages(context, None)
    if isinstance(images, ImagesAdapter):
        ImagesAdapter.image.update_metadata(images)


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.relation.interfaces.IReferenceProvider)
def image_references(context):
    images = zeit.content.image.interfaces.IImages(context, None)
    if images is None:
        return None
    image = images.image
    if image is None:
        return ()
    return (image,)


@zope.component.adapter(zeit.content.image.interfaces.IImageGroup)
@zope.interface.implementer(zeit.content.image.interfaces.IReferences)
class References:
    def __init__(self, context):
        self.context = context

    @property
    def references(self):
        relations = zope.component.getUtility(zeit.cms.relation.interfaces.IRelations)
        relating_objects = relations.get_relations(self.context)
        return tuple(relating_objects)
