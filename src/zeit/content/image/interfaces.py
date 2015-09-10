# coding: utf8
from zeit.cms.i18n import MessageFactory as _
import PIL.Image
import zc.form.field
import zc.sourcefactory.contextual
import zeit.cms.content.contentsource
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workingcopy.interfaces
import zope.file.interfaces
import zope.schema


IMAGE_NAMESPACE = 'http://namespaces.zeit.de/CMS/image'


class ImageProcessingError(TypeError):
    """An error raised it's not possible to process the Image."""


class IImageType(zeit.cms.interfaces.ICMSContentType):
    """The interface of image interfaces."""


class AlignmentSource(zeit.cms.content.sources.SimpleFixedValueSource):

    values = (u'left', u'center', u'right')


class ILinkField(zope.interface.Interface):
    """Marker interface so we can register a custom widget for this field."""


class IImageMetadata(zope.interface.Interface):

    title = zope.schema.TextLine(
        title=_("Image title"),
        default=u'',
        required=False)

    year = zope.schema.Int(
        title=_("Year"),
        min=1900,
        max=2100,
        required=False)

    volume = zope.schema.Int(
        title=_("Volume"),
        min=1,
        max=53,
        required=False)

    copyrights = zope.schema.Tuple(
        title=_("Copyrights"),
        default=((u'©', None, False),),
        missing_value=(),
        required=False,
        value_type=zc.form.field.Combination(
            (zope.schema.TextLine(
                title=_("Copyright"),
                min_length=3,
                required=True),
             zope.schema.URI(
                 title=_('Link'),
                 description=_('Link to copyright holder'),
                 required=False),
             zope.schema.Bool(
                 title=_('set nofollow'),
                required=False))))

    alt = zope.schema.TextLine(
        title=_("Alternative text"),
        description=_("Enter a textual description of the image"),
        default=u'',
        required=False)

    caption = zope.schema.Text(
        title=_("Image sub text"),
        default=u'',
        required=False)

    links_to = zope.schema.URI(
        title=_('Links to'),
        description=_('Enter a URL this image should link to.'),
        required=False)
    # XXX Disabled because the frontend does not interpret rewritten links
    # correctly yet.
    # zope.interface.alsoProvides(links_to, ILinkField)

    alignment = zope.schema.Choice(
        title=_('Alignment'),
        source=AlignmentSource(),
        default='left')

    acquire_metadata = zope.schema.Bool(
        title=u'True if metadata should be acquired from the parent.')


class IImage(zeit.cms.interfaces.IAsset,
             zeit.cms.repository.interfaces.IDAVContent,
             zope.file.interfaces.IFile):
    """Image."""

    def getImageSize():
        """return tuple (width, heigth) of image."""

    format = zope.interface.Attribute(
        'Our mimeType formatted as a PIL-compatible format (e.g. JPEG, PNG)')

    ratio = zope.interface.Attribute('width/height')


class ITransform(zope.interface.Interface):

    def thumbnail(width, height, filter=PIL.Image.ANTIALIAS):
        """Create a thumbnail version of the image.

        returns IImage object.
        """

    def resize(width=None, height=None, filter=PIL.Image.ANTIALIAS):
        """Create a resized version of the image.

        returns IImage object.
        raises TypeError of both width and height are ommited.

        """

    def create_variant_image(variant, size=None):
        """Create a cropped version of the image, using the configuration
        information (focus point, zoom, etc.) of the given IVariant.

        A tuple `size` can be given to resize the resulting image to a certain
        size.

        returns IImage object.
        """


class IPersistentThumbnail(IImage):
    """Persistent thumbnail version of an image."""


class IThumbnailFolder(zope.interface.Interface):
    """The folder where to find thumbnails for an image."""


class MasterImageSource(
    zc.sourcefactory.contextual.BasicContextualSourceFactory):

    def getValues(self, context):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        for name in repository.getContent(context.uniqueId):
            yield name


class IImageGroup(zeit.cms.repository.interfaces.ICollection,
                  zeit.cms.interfaces.IAsset,
                  zeit.cms.repository.interfaces.IDAVContent):
    """An image group groups images with the same motif together."""

    master_image = zope.schema.Choice(
        title=_('Master image'),
        source=MasterImageSource())

    variants = zope.schema.Dict(
        title=_('Setting for variants'))

    def variant_url(name, width=None, height=None, thumbnail=False):
        """Return an URL path to the variant with the given name that matches
        the width/height requirements most closely.

        This is only the path so clients can prepend the proper hostname etc.,
        so e.g. vivi can generate URLs that point to its own repository as well
        as to www.zeit.de, for example.

        If thumbnail is True, return a path for an image that was generated
        by a downsampled version instead of the full master image.

        If a `variant-secret` is configured in the zeit.content.image product
        config, adds a signed hash of width and height to the URL, to prevent
        URL spoofing.
        """

    def create_variant_image(key, source=None):
        """For internal use: dynamically create a cropped version of the source
        image, according to the settings of the variant determined by key.
        """


class IRepositoryImageGroup(IImageGroup):
    """An image group in the repository.  It contains images.

    """


class ILocalImageGroup(IImageGroup,
                       zeit.cms.workingcopy.interfaces.ILocalContent):
    """Local version of an image group.

    The local version only holds the metadata, therefore it is not a container.
    """


class IVariants(zope.interface.common.mapping.IEnumerableMapping):
    """Object-oriented access to IImageGroup.variants."""


class IVariant(zope.interface.Interface):

    id = zope.schema.TextLine(description=u'Unique Variant name')
    name = zope.schema.TextLine(description=u'Grouping of Variant sizes')
    display_name = zope.schema.TextLine(description=u'Displayed name')
    focus_x = zope.schema.Float(
        description=u'Position of the focus point relative to image width')
    focus_y = zope.schema.Float(
        description=u'Position of the focus point relative to image height')
    zoom = zope.schema.Float(
        description=u'Zoom factor used, i.e. 1 for no zoom')
    aspect_ratio = zope.schema.TextLine(
        description=u"String representation of ratio as X:Y, e.g. 16:9")
    max_size = zope.schema.TextLine(
        description=u"Maximum width / height of this Variant, e.g. 160x90")
    brightness = zope.schema.Float(
        description=u'Factor to enhance brightness, 1.0 for original value')
    fallback_size = zope.schema.TextLine(
        description=u"Fallback width / height, e.g. 1200x514")

    ratio = zope.interface.Attribute(
        'Float representation of ratio')
    max_width = zope.interface.Attribute(
        'Shorthand to access width of max_size')
    max_height = zope.interface.Attribute(
        'Shorthand to access height of max_size')
    fallback_width = zope.interface.Attribute(
        'Shorthand to access width of fallback_size')
    fallback_height = zope.interface.Attribute(
        'Shorthand to access height of fallback_size')
    relative_image_path = zope.interface.Attribute(
        'Image path relative to the ImageGroup the Variant lives in')
    is_default = zope.interface.Attribute(
        'Bool whether this Variant represents the default configuration')

    legacy_name = zope.interface.Attribute(
        'If applicable, the legacy name this Variant was mapped from')


class IImageSource(zope.interface.common.mapping.IEnumerableMapping):
    """A source for images."""


class ImageSource(zeit.cms.content.contentsource.CMSContentSource):

    zope.interface.implements(IImageSource)
    check_interfaces = IImageType
    name = 'images'

imageSource = ImageSource()


class BareImageSource(zeit.cms.content.contentsource.CMSContentSource):

    zope.interface.implements(IImageSource)
    check_interfaces = (IImage,)
    name = 'bare-images'

bareImageSource = BareImageSource()


class ImageGroupSource(zeit.cms.content.contentsource.CMSContentSource):

    zope.interface.implements(IImageSource)
    check_interfaces = (IImageGroup,)
    name = 'image-groups'

    def __contains__(self, value):
        # backwards compatibility: IImages used to contain both IImage and
        # IImageGroup, so there might still be content with IImage around
        # which needs to be accessible.
        if IImage.providedBy(value):
            return True
        return super(ImageGroupSource, self).__contains__(value)

imageGroupSource = ImageGroupSource()


class IThumbnails(zope.container.interfaces.IReadContainer):
    """Traverser to access smaller images via /thumbnails"""

    source_image = zope.schema.Choice(source=bareImageSource)


class IImages(zope.interface.Interface):
    """An object which references images."""

    image = zope.schema.Choice(
        title=_('Image'),
        description=_("Drag an image group here"),
        required=False,
        source=imageGroupSource)


class IReferences(zope.interface.Interface):

    references = zope.schema.Tuple(
        title=_('Objects using this image'),
        readonly=True,
        value_type=zope.schema.Choice(
            source=zeit.cms.content.contentsource.cmsContentSource))


class IMasterImage(zope.interface.Interface):
    """Marks an image in an image group as master for the other images."""


class IImageReference(zeit.cms.content.interfaces.IReference,
                      IImageMetadata):
    """Reference to an image, allows overriding metadata locally for the
    referring content object."""
