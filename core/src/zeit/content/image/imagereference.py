import grokcore.component as grok
import zeit.cms.checkout.interfaces
import zeit.cms.content.property
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

    image = zeit.cms.content.reference.SingleResource(
        '.head.image', 'image')

    fill_color = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.head.image', 'fill_color',
        zeit.content.image.interfaces.IImages['fill_color'])


class LocalOverride(object):

    def __init__(self, name):
        self.name = name

    def __get__(self, instance, class_):
        if instance is None:
            return self
        return getattr(instance, '_%s_local' % self.name)

    def __set__(self, instance, value):
        __traceback_info__ = (self.name, value)
        setattr(instance, '_%s_local' % self.name, value)
        # XXX Maybe fall back to original value (from instance.target) when
        # value is None? Or is it enough that we wait until checkin,
        # when update_metadata will do that anyway?
        setattr(instance, '_%s_original' % self.name, value)


class ImageReference(zeit.cms.content.reference.Reference):

    grok.name('image')
    grok.implements(zeit.content.image.interfaces.IImageReference)
    grok.provides(zeit.cms.content.interfaces.IReference)

    # XXX The *_original XML paths must be kept in sync with
    # z.c.image.metadata.XMLReferenceUpdater

    _title_original = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'title',
        zeit.content.image.interfaces.IImageMetadata['title'])
    _title_local = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'title_local',
        zeit.content.image.interfaces.IImageReference['title'])

    _alt_original = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'alt',
        zeit.content.image.interfaces.IImageMetadata['alt'])
    _alt_local = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'alt_local',
        zeit.content.image.interfaces.IImageReference['alt'])

    _caption_original = zeit.cms.content.property.ObjectPathProperty(
        '.bu', zeit.content.image.interfaces.IImageMetadata['caption'])
    _caption_local = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'caption_local',
        zeit.content.image.interfaces.IImageReference['caption'])

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

    title = LocalOverride('title')
    alt = LocalOverride('alt')
    caption = LocalOverride('caption')

    def update_metadata(self, suppress_errors=False):
        super(ImageReference, self).update_metadata(suppress_errors)
        for name in zope.schema.getFieldNames(
                zeit.content.image.interfaces.IImageMetadata):
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
                image, zeit.cms.content.interfaces.IXMLReference, name='image')
            if image_node is None:
                if not self.suppress_errors:
                    raise ValueError(
                        ("Could not create xml reference 'image' for %s which "
                         "is referenced in %s.") % (
                             image.uniqueId, self.context.uniqueId))
            else:
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
    ImagesAdapter.image.update_metadata(images)


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
