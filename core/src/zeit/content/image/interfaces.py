# coding: utf8
import PIL.Image
import zc.form.field
import zc.form.interfaces
import zc.sourcefactory.contextual
import zc.sourcefactory.factories
import zope.file.interfaces
import zope.interface
import zope.schema

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.interfaces import CONFIG_CACHE
import zeit.cms.content.contentsource
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workingcopy.interfaces


IMAGE_NAMESPACE = 'http://namespaces.zeit.de/CMS/image'
AVAILABLE_MIME_TYPES = ['image/jpeg', 'image/png']
AVAILABLE_PILLOW_TYPES = [x.replace('image/', '').upper() for x in AVAILABLE_MIME_TYPES]


class ImageProcessingError(TypeError):
    """An error raised it's not possible to process the Image."""


class IImageType(zeit.cms.interfaces.ICMSContentType):
    """The interface of image interfaces."""


class CopyrightCompanySource(zeit.cms.content.sources.XMLSource):
    product_configuration = 'zeit.content.image'
    config_url = 'copyright-company-source'
    default_filename = 'image-copyright-company.xml'

    def getValues(self, context):
        tree = self._get_tree()
        return [str(node) for node in tree.iterchildren('*') if self.isAvailable(node, context)]

    def getTitle(self, context, value):
        return value


COPYRIGHT_COMPANY_SOURCE = CopyrightCompanySource()


class IImageMetadata(zope.interface.Interface):
    title = zope.schema.TextLine(title=_('Image title'), default='', required=False)

    origin = zope.schema.TextLine(title=_('Origin'), default='', required=False)

    copyright = zc.form.field.Combination(
        (
            zope.schema.TextLine(title=_('Photographer'), required=False),
            zope.schema.Choice(
                title=_('Image company'), source=COPYRIGHT_COMPANY_SOURCE, required=True
            ),
            zope.schema.TextLine(
                title=_('Copyright freetext'),
                description=_('Copyright holder that is not part ' 'of image company list'),
                required=False,
            ),
            zope.schema.URI(
                title=_('Link'), description=_('Link to copyright holder'), required=False
            ),
            zope.schema.Bool(title=_('set nofollow'), required=False),
        ),
        default=None,
        title=_('Copyrights'),
        missing_value=None,
    )

    single_purchase = zope.schema.Bool(title=_('Single purchase'), required=False)

    external_id = zope.schema.TextLine(title=_('External company ID'), required=False)

    mdb_id = zope.schema.TextLine(title=_('InterRed MDB ID'), required=False, readonly=True)

    alt = zope.schema.TextLine(
        title=_('Alternative text'),
        description=_('Enter a textual description of the image'),
        default='',
        required=False,
    )

    caption = zope.schema.Text(title=_('Image sub text'), default='', required=False)

    links_to = zope.schema.URI(
        title=_('Links to'), description=_('Enter a URL this image should link to.'), required=False
    )

    nofollow = zope.schema.Bool(title=_('set nofollow'), required=False, default=False)

    acquire_metadata = zope.schema.Bool(
        title='True if metadata should be acquired from the parent.'
    )


class IImage(
    zeit.cms.interfaces.IAsset,
    zeit.cms.repository.interfaces.IDAVContent,
    zope.file.interfaces.IFile,
):
    """Image."""

    def getImageSize():
        """return tuple (width, heigth) of image."""

    format = zope.interface.Attribute(
        'Our mimeType formatted as a PIL-compatible format (e.g. JPEG, PNG)'
    )

    ratio = zope.interface.Attribute('width/height')


class ITransform(zope.interface.Interface):
    def thumbnail(width, height, filter=PIL.Image.Resampling.LANCZOS):
        """Create a thumbnail version of the image.

        returns IImage object.
        """

    def resize(width=None, height=None, filter=PIL.Image.Resampling.LANCZOS):
        """Create a resized version of the image.

        returns IImage object.
        raises TypeError of both width and height are ommited.

        """

    def create_variant_image(variant, size=None, fill=None):
        """Create a cropped version of the image, using the configuration
        information (focus point, zoom, etc.) of the given IVariant.

        A tuple `size` can be given to resize the resulting image to a certain
        size. For images with an alpha channel (mostly: PNG), `fill` can
        specify a RGB hexadecimal color code, transparent parts will be
        filled with that color.

        returns IImage object.

        """


class IPersistentThumbnail(IImage):
    """Persistent thumbnail version of an image."""


class IThumbnailFolder(zope.interface.Interface):
    """The folder where to find thumbnails for an image."""


class MasterImageSource(zc.sourcefactory.contextual.BasicContextualSourceFactory):
    def getValues(self, context):
        """List names of images inside ImageGroup."""
        # Sadly zc.form.field.Combination does not bind it's field to the right
        # context, thus fix the context if necessary.
        if zc.form.interfaces.ICombinationField.providedBy(context):
            context = context.context
        repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        for name in repository.getContent(context.uniqueId):
            yield name


INFOGRAPHIC_DISPLAY_TYPE = 'infographic'


class DisplayTypeSource(zeit.cms.content.sources.XMLSource):
    product_configuration = 'zeit.content.image'
    config_url = 'display-type-source'
    default_filename = 'image-display-types.xml'
    attribute = 'id'


class ViewportSource(zeit.cms.content.sources.SimpleFixedValueSource):
    values = {
        'desktop': _('viewport-desktop'),
        'mobile': _('viewport-mobile'),
    }


VIEWPORT_SOURCE = ViewportSource()


class DuplicateViewport(zope.schema.ValidationError):
    __doc__ = _('Viewport was used multiple times')


class DuplicateImage(zope.schema.ValidationError):
    __doc__ = _('Image was used multiple times')


def unique_viewport_and_master_image(value):
    """Ensure that any `viewport` and any `master_image` appears only once.

    The setting `unique = True` only ensures that each *combination* is unique.
    But we actually want to avoid that any viewport or any master_image is
    chosen multiple times, no matter in which combination.

    """
    viewports = set()
    master_images = set()
    for item in value:
        if item is None:
            # XXX Tuple widget uses None for invalid items, regardless of its
            # value_type, which in our case would expect a 2-element tuple.
            continue
        viewport, master_image = item
        if viewport in viewports:
            raise DuplicateViewport(viewport)
        if master_image in master_images:
            raise DuplicateImage(master_image)
        viewports.add(viewport)
        master_images.add(master_image)
    return True


class IImageGroup(
    zeit.cms.repository.interfaces.ICollection,
    zeit.cms.interfaces.IAsset,
    zeit.cms.repository.interfaces.IDAVContent,
):
    """An image group groups images with the same motif together."""

    __name__ = zope.schema.TextLine(
        title=_('File name of image group'),
        readonly=True,
        constraint=zeit.cms.interfaces.valid_name,
    )

    master_image = zope.interface.Attribute('Name of the master image')

    master_images = zope.schema.Tuple(
        title=_('Mapping of viewport to master image'),
        unique=True,
        min_length=1,
        missing_value=(),
        constraint=unique_viewport_and_master_image,
        value_type=zc.form.field.Combination(
            (
                zope.schema.Choice(title=_('Viewport'), source=VIEWPORT_SOURCE),
                zope.schema.Choice(title=_('Image file'), source=MasterImageSource()),
            )
        ),
    )

    variants = zope.schema.Dict(title=_('Setting for variants'))

    display_type = zope.schema.Choice(
        title=_('Display Type'), source=DisplayTypeSource(), default='imagegroup', required=True
    )

    def variant_url(name, width=None, height=None, fill_color=None, thumbnail=False):
        """Return an URL path to the variant with the given name that matches
        the width/height requirements most closely.

        This is only the path so clients can prepend the proper hostname etc.,
        so e.g. vivi can generate URLs that point to its own repository as well
        as to www.zeit.de, for example.

        Optionally a fill_color can be given (for images with an alpha channel)

        If thumbnail is True, return a path for an image that was generated
        by a downsampled version instead of the full master image.
        """

    def create_variant_image(key, source=None):
        """For internal use: dynamically create a cropped version of the source
        image, according to the settings of the variant determined by key.
        """

    def master_image_for_viewport(viewport):
        """Returns the master image for the given viewport. If none is found,
        returns IMasterImage(self) instead.
        """


class IRepositoryImageGroup(IImageGroup):
    """An image group in the repository.  It contains images."""


class ILocalImageGroup(IImageGroup, zeit.cms.workingcopy.interfaces.ILocalContent):
    """Local version of an image group.

    The local version only holds the metadata, therefore it is not a container.
    """


class IVariants(zope.interface.common.mapping.IEnumerableMapping):
    """Object-oriented access to IImageGroup.variants."""


class IVariant(zope.interface.Interface):
    id = zope.schema.TextLine(description='Unique Variant name')
    name = zope.schema.TextLine(description='Grouping of Variant sizes')
    display_name = zope.schema.TextLine(description='Displayed name')
    focus_x = zope.schema.Float(description='Position of the focus point relative to image width')
    focus_y = zope.schema.Float(description='Position of the focus point relative to image height')
    zoom = zope.schema.Float(description='Zoom factor used, i.e. 1 for no zoom')
    aspect_ratio = zope.schema.TextLine(
        description='String representation of ratio as X:Y, e.g. 16:9. '
        'Can be set to `original`, to use width/height of image.'
    )
    max_size = zope.schema.TextLine(
        description='Maximum width / height of this Variant, e.g. 160x90'
    )
    brightness = zope.schema.Float(
        description='Factor to enhance brightness, 1.0 for original value'
    )
    contrast = zope.schema.Float(description='Factor to enhance contrast, 1.0 for original value')
    saturation = zope.schema.Float(
        description='Factor to enhance saturation, 1.0 for original value'
    )
    sharpness = zope.schema.Float(description='Factor to enhance sharpness, 1.0 for original value')
    fallback_size = zope.schema.TextLine(
        description='Fallback width / height, e.g. 1200x514. '
        'Used by Friedbert to limit the size of large variants.'
    )

    ratio = zope.interface.Attribute('Float representation of ratio')
    max_width = zope.interface.Attribute('Shorthand to access width of max_size')
    max_height = zope.interface.Attribute('Shorthand to access height of max_size')
    fallback_width = zope.interface.Attribute('Shorthand to access width of fallback_size')
    fallback_height = zope.interface.Attribute('Shorthand to access height of fallback_size')
    relative_image_path = zope.interface.Attribute(
        'Image path relative to the ImageGroup the Variant lives in'
    )
    is_default = zope.interface.Attribute(
        'Bool whether this Variant represents the default configuration'
    )

    legacy_name = zope.interface.Attribute(
        'If applicable, the legacy name this Variant was mapped from'
    )
    legacy_size = zope.interface.Attribute(
        'If applicable, a [width, height] setting to use if no size'
        ' was passed in through the URL'
    )


class IImageSource(zope.interface.common.mapping.IEnumerableMapping):
    """A source for images."""


@zope.interface.implementer(IImageSource)
class ImageSource(zeit.cms.content.contentsource.CMSContentSource):
    check_interfaces = IImageType
    name = 'images'


imageSource = ImageSource()


@zope.interface.implementer(IImageSource)
class BareImageSource(zeit.cms.content.contentsource.CMSContentSource):
    check_interfaces = (IImage,)
    name = 'bare-images'


bareImageSource = BareImageSource()


@zope.interface.implementer(IImageSource)
class ImageGroupSource(zeit.cms.content.contentsource.CMSContentSource):
    check_interfaces = (IImageGroup,)
    name = 'image-groups'


imageGroupSource = ImageGroupSource()


class IThumbnails(zope.container.interfaces.IReadContainer):
    """Traverser to access smaller images via /thumbnails"""

    source_image = zope.schema.Choice(source=bareImageSource)


class IImages(zope.interface.Interface):
    """An object which references images."""

    image = zope.schema.Choice(
        title=_('Image group'),
        description=_('Drag an image group here'),
        required=False,
        source=imageGroupSource,
    )

    fill_color = zope.schema.TextLine(
        title=_('Alpha channel fill color'),
        required=False,
        max_length=6,
        constraint=zeit.cms.content.interfaces.hex_literal,
    )


class IReferences(zope.interface.Interface):
    references = zope.schema.Tuple(
        title=_('Objects using this image'),
        readonly=True,
        value_type=zope.schema.Choice(source=zeit.cms.content.contentsource.cmsContentSource),
    )


class IMasterImage(zope.interface.Interface):
    """Marks an image in an image group as master for the other images."""


class IImageReference(zeit.cms.content.interfaces.IReference, IImageMetadata):
    """Reference to an image, allows overriding metadata locally for the
    referring content object."""


class IMDB(zope.interface.Interface):
    """InterRed MDB API"""

    def get_metadata(mdb_id):
        """Returns a dict of image metadata."""

    def get_body(mdb_id):
        """Returns a file-like object containing the raw image data."""


class EncoderParameters(zeit.cms.content.sources.CachedXMLBase):
    product_configuration = 'zeit.content.image'
    config_url = 'encoder-parameters'
    default_filename = 'image-encoders.xml'

    def find(self, typ):
        return self.values().get(typ) or {}

    @CONFIG_CACHE.cache_on_arguments()
    def values(self):
        result = {}
        for encoder in self._get_tree().iterfind('encoder'):
            result[encoder.get('name')] = params = {}
            for node in encoder.iterfind('param'):
                params[node.get('name')] = node.pyval
        return result


ENCODER_PARAMETERS = EncoderParameters()
