from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.contentsource
import zeit.cms.content.field
import zeit.cms.content.interfaces
import zeit.content.gallery.source
import zeit.content.image.interfaces
import zeit.crop.source
import zeit.wysiwyg.interfaces
import zope.container.interfaces
import zope.schema


DAV_NAMESPACE = 'http://namespaces.zeit.de/CMS/zeit.content.gallery'


class IGalleryFolderSource(zeit.cms.content.interfaces.ICMSContentSource):
    """A source for gallery folders."""


@zope.interface.implementer_only(IGalleryFolderSource)
class GalleryFolderSource(zeit.cms.content.contentsource.FolderSource):

    name = 'gallery-folders'


galleryFolderSource = GalleryFolderSource()


class IGalleryMetadata(zeit.cms.content.interfaces.ICommonMetadata):
    """Center page metadata."""

    type = zope.schema.Choice(
        title=_('Gallery type'),
        source=zeit.content.gallery.source.GalleryTypeSource(),
        default='standalone')

    image_folder = zope.schema.Choice(
        title=_("Image folder"),
        description=_("Folder containing images to display in the gallery."),
        source=galleryFolderSource)


class IReadGallery(
        IGalleryMetadata,
        zeit.cms.content.interfaces.IXMLContent,
        zope.container.interfaces.IReadContainer):
    """Read methods for gallery."""


class IWriteGallery(zope.container.interfaces.IWriteContainer):
    """Write methods for gallery."""

    def reload_image_folder():
        """Reload the image folder

        Calling this removes entries from the gallery where the referenced
        object does no longer exist and adds entries for new object.

        """

    def updateOrder(order):
        """Revise the order of keys, replacing the current ordering.

        order is a list or a tuple containing the set of existing keys in
        the new order. `order` must contain ``len(keys())`` items and cannot
        contain duplicate keys.

        Raises ``ValueError`` if order contains an invalid set of keys.
        """


class IGallery(IReadGallery, IWriteGallery):
    """An image gallery"""


class IGalleryEntry(zope.interface.Interface):
    """One image in the gallery."""

    image = zope.schema.Object(zeit.content.image.interfaces.IImage)
    thumbnail = zope.schema.Object(zeit.content.image.interfaces.IImage)

    crops = zope.interface.Attribute(
        'List of IGalleryEntry that are crops of this entry')

    is_crop_of = zope.schema.TextLine(
        title=_('Is a cropped image of'),
        required=False,
        readonly=True)

    title = zope.schema.TextLine(
        title=_('Title'),
        required=False)

    # XXX deprecated, only kept around so that existing text can still be
    # accessed (see #8858)
    text = zeit.cms.content.field.XMLTree(
        title=_("Text"),
        required=False)

    layout = zope.schema.Choice(
        title=_('Layout'),
        required=False,
        source=zeit.content.gallery.source.LayoutSource())

    caption = zope.schema.Text(
        title=_("Image caption"),
        description=_('gallery-image-caption-description'),
        required=False,
        missing_value='')


class GallerySource(zeit.cms.content.contentsource.CMSContentSource):

    name = 'zeit.content.gallery'
    check_interfaces = (IGallery,)


gallerySource = GallerySource()


class IGalleryReference(zope.interface.Interface):

    gallery = zope.schema.Choice(
        title=_('Image gallery'),
        description=_("Drag a gallery here"),
        required=False,
        source=gallerySource)


class ScaleSource(zeit.crop.source.ScaleSource):

    product_configuration = 'zeit.content.gallery'


class IVisibleEntryCount(zope.interface.Interface):
    """Count of gallery entries whose layout is not hidden"""
