# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.contentsource
import zeit.cms.content.field
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.gallery.source
import zeit.content.image.interfaces
import zope.schema


class IGalleryFolderSource(zeit.cms.content.interfaces.ICMSContentSource):
    """A source for gallery folders."""


class GalleryFolderSource(zeit.cms.content.contentsource.FolderSource):

    zope.interface.implementsOnly(IGalleryFolderSource)
    name = u'gallery-folders'


galleryFolderSource = GalleryFolderSource()


class IGalleryMetadata(zeit.cms.content.interfaces.ICommonMetadata):
    """Center page metadata."""

    image_folder = zope.schema.Choice(
        title=_("Image folder"),
        description=_("Folder containing images to display in the gallery."),
        source=galleryFolderSource)


class IReadGallery(
    IGalleryMetadata,
    zeit.cms.content.interfaces.IXMLContent,
    zope.app.container.interfaces.IReadContainer):
    """Read methods for gallery."""


class IWriteGallery(zope.app.container.interfaces.IWriteContainer):
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

    text = zeit.cms.content.field.XMLTree(
        title=_("Text"),
        required=False)

    layout = zope.schema.Choice(
        title=_('Layout'),
        required=False,
        source=zeit.content.gallery.source.LayoutSource())

    hidden = zope.schema.Bool(
        title=_('Hidden'),
        required=True)

    caption = zeit.cms.content.field.XMLSnippet(
        title=_("Image caption"),
        description=_('gallery-image-caption-description'),
        required=False)


class GallerySource(zeit.cms.content.contentsource.CMSContentSource):

    name = 'zeit.content.gallery'

    def verify_interface(self, value):
        return IGallery.providedBy(value)

gallerySource = GallerySource()


class IGalleryReference(zope.interface.Interface):

    gallery = zope.schema.Choice(
        title=_('Image gallery as box'),
        required=False,
        source=gallerySource)

    embedded_gallery = zope.schema.Choice(
        title=_('Embedded image gallery'),
        required=False,
        source=gallerySource)
