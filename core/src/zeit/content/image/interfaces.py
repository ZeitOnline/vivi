# coding: utf8
# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zc.form.field
import zc.sourcefactory.basic
import zope.file.interfaces
import zope.schema

import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.workingcopy.interfaces
import zeit.cms.content.contentsource
from zeit.cms.i18n import MessageFactory as _


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
        return self.titles[value]


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
        default=((u'ZEIT ONLINE', 'http://www.zeit.de/'),),
        missing_value=(),
        required=False,
        value_type=zc.form.field.Combination(
            (zope.schema.TextLine(
                title=_("Copyright"),
                default=u"©",
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


class IImage(zeit.cms.interfaces.IAsset,
             zope.file.interfaces.IFile):
    """Image."""

    def getImageSize():
        """return tuple (width, heigth) of image."""


class ITransform(zope.interface.Interface):

    def thumbnail(width, height):
        """Create a thumbnail version of the image.

        returns IImage object.
        """

    def resize(width=None, height=None):
        """Create a resized version of the image.

        returns IImage object.
        raises TypeError of both width and height are ommited.

        """

class IPersistentThumbnail(IImage):
    """Persistent thumbnail version of an image."""


class IThumbnailFolder(zope.interface.Interface):
    """The folder where to find thumbnails for an image."""


class IImageGroup(zeit.cms.interfaces.IAsset):
    """An image group groups images with the same motif together."""


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
