from zeit.cms.content.interfaces import WRITEABLE_ALWAYS
import grokcore.component as grok
import lxml.objectify
import zeit.cms.content.dav
import zeit.content.image.interfaces
import zeit.content.image.image
import zope.component
import zope.interface
import zope.schema


@zope.interface.implementer(zeit.content.image.interfaces.IImageMetadata)
class ImageMetadata:

    zeit.cms.content.dav.mapProperties(
        zeit.content.image.interfaces.IImageMetadata,
        zeit.content.image.interfaces.IMAGE_NAMESPACE,
        ('alt', 'caption', 'links_to', 'nofollow', 'origin', 'mdb_id',
            'single_purchase'))
    zeit.cms.content.dav.mapProperties(
        zeit.content.image.interfaces.IImageMetadata,
        'http://namespaces.zeit.de/CMS/document',
        ('title',))

    zeit.cms.content.dav.mapProperties(
        zeit.content.image.interfaces.IImageMetadata,
        zeit.content.image.interfaces.IMAGE_NAMESPACE,
        ('external_id',), writeable=WRITEABLE_ALWAYS)

    # XXX Since ZON-4106 there should only be one copyright and the api has
    # been adjusted to 'copyright'. For bw-compat reasons the DAV property is
    # still called 'copyrights'
    _copyrights = zeit.cms.content.dav.DAVProperty(
        zeit.content.image.interfaces.IImageMetadata['copyright'],
        'http://namespaces.zeit.de/CMS/document', 'copyrights',
        use_default=True)

    @property
    def copyright(self):
        value = self._copyrights
        if not value:
            return
        # Migration for exactly one copyright (ZON-4106)
        if type(value[0]) is tuple:
            value = value[0]
        # Migration for nofollow (VIV-104)
        if len(value) == 2:
            value = (value[0], None, None, value[1], False)
        # Migration for companies (ZON-3174)
        if len(value) == 3:
            value = (value[0], None, None, value[1], value[2])
        return value

    @copyright.setter
    def copyright(self, value):
        self._copyrights = value

    zeit.cms.content.dav.mapProperties(
        zeit.content.image.interfaces.IImageMetadata,
        'http://namespaces.zeit.de/CMS/meta',
        ('acquire_metadata',))

    def __init__(self, context):
        self.context = context


@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
@zope.component.adapter(ImageMetadata)
def metadata_webdav_properties(context):
    return zeit.connector.interfaces.IWebDAVProperties(
        context.context)


@grok.implementer(zeit.content.image.interfaces.IImageMetadata)
@grok.adapter(zeit.content.image.interfaces.IImage)
def metadata_for_image(image):
    metadata = ImageMetadata(image)
    # Be sure to get the image in the repository
    parent = None
    if image.uniqueId:
        image_in_repository = parent = zeit.cms.interfaces.ICMSContent(
            image.uniqueId, None)
        if image_in_repository is not None:
            parent = image_in_repository.__parent__
    if zeit.content.image.interfaces.IImageGroup.providedBy(parent):
        # The image *is* in an image group.
        if metadata.acquire_metadata is None or metadata.acquire_metadata:
            group_metadata = zeit.content.image.interfaces.IImageMetadata(
                parent)
            if zeit.cms.workingcopy.interfaces.ILocalContent.providedBy(image):
                for name, field in zope.schema.getFieldsInOrder(
                        zeit.content.image.interfaces.IImageMetadata):
                    value = getattr(group_metadata, name, None)
                    setattr(metadata, name, value)
                metadata.acquire_metadata = False
            else:
                # For repository content return the metadata of the group.
                metadata = group_metadata

    return metadata


@grok.adapter(zeit.content.image.image.TemporaryImage)
@grok.implementer(zeit.content.image.interfaces.IImageMetadata)
def metadata_for_synthetic(context):
    return zeit.content.image.interfaces.IImageMetadata(context.__parent__)


class XMLReferenceUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):

    target_iface = zeit.content.image.interfaces.IImageMetadata

    def update_with_context(self, entry, context):
        def set_attribute(name, value):
            if value:
                entry.set(name, value)
            else:
                entry.attrib.pop(name, None)

        set_attribute('origin', context.origin)
        set_attribute('title', context.title)
        set_attribute('alt', context.alt)

        # XXX This is really ugly: XMLReference type 'related' uses href for
        # the uniqueId, but type 'image' uses 'src' or 'base-id' instead, and
        # reuses 'href' for the link information. And since XMLReferenceUpdater
        # is called for all types of reference, we need to handle both ways.
        if entry.get('src') or entry.get('base-id'):
            set_attribute('href', context.links_to)

        if context.nofollow:
            set_attribute('rel', 'nofollow')

        entry['bu'] = context.caption or None

        for child in entry.iterchildren('copyright'):
            entry.remove(child)

        if context.copyright is None:
            return
        text, company, freetext, link, nofollow = context.copyright
        node = lxml.objectify.E.copyright(text)
        if link:
            node.set('link', link)
            if nofollow:
                node.set('rel', 'nofollow')
        entry.append(node)
