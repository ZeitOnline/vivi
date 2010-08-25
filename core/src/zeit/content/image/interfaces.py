# coding: utf8
# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import PIL.Image
import zc.form.field
import zc.sourcefactory.basic
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


class AlignmentSource(zc.sourcefactory.basic.BasicSourceFactory):

    values = ((u'left', _('left')),
              (u'center', _('center')),
              (u'right', _('right')))

    def __init__(self):
        self.titles = dict(self.values)
        self.values = tuple(v[0] for v in self.values)

    def getValues(self):
        return self.values

    def getTitle(self, value):
        return self.titles.get(value, value)


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
        default=((u'©', None),),
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
                required=False))))

    alt = zope.schema.TextLine(
        title=_("Alternative text"),
        description=_("Enter a textual description of the image"),
        default=u'',
        required=False)

    caption = zeit.cms.content.field.XMLSnippet(
        title=_("Image sub text"),
        default=u'',
        required=False)

    links_to = zope.schema.URI(
        title=_('Links to'),
        description=_('Enter a URL this image should link to.'),
        required=False)

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


class IImageGroup(zeit.cms.interfaces.IAsset,
                  zeit.cms.repository.interfaces.IDAVContent):
    """An image group groups images with the same motif together."""

    master_image = zope.schema.Choice(
        title=_('Master image'),
        source=MasterImageSource(),
        required=False)


class IRepositoryImageGroup(IImageGroup,
                            zeit.cms.repository.interfaces.ICollection):
    """An image group in the repository.  It contains images.

    """


class ILocalImageGroup(IImageGroup,
                       zeit.cms.workingcopy.interfaces.ILocalContent):
    """Local version of an image group.

    The local version only holds the metadata, therefore it is not a container.
    """


class IImageSource(zeit.cms.content.interfaces.ICMSContentSource):
    """A source for images."""


class ImageSource(zeit.cms.content.contentsource.CMSContentSource):

    zope.interface.implements(IImageSource)
    check_interfaces = IImageType
    name = 'images'

imageSource = ImageSource()


class IImages(zope.interface.Interface):
    """An object which references images."""

    images = zope.schema.Tuple(
        title=_('Images'),
        required=False,
        default=(),
        value_type=zope.schema.Choice(
            source=imageSource))


class IReferences(zope.interface.Interface):

    references = zope.schema.Tuple(
        title=_('Objects using this image'),
        readonly=True,
        value_type=zope.schema.Choice(
            source=zeit.cms.content.contentsource.cmsContentSource))


class IMasterImage(zope.interface.Interface):
    """Marks an image in an image group as master for the other images."""
