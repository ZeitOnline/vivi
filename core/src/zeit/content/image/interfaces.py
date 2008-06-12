# coding: utf8
# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.schema

import zope.app.file.interfaces

import zc.form.field

import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.workingcopy.interfaces
import zeit.cms.content.contentsource
from zeit.cms.i18n import MessageFactory as _


class ImageProcessingError(TypeError):
    """An error raised it's not possible to process the Image."""


class IImageType(zeit.cms.interfaces.ICMSContentType):
    """The interface of image interfaces."""


class IImageMetadata(zope.interface.Interface):

    expires = zope.schema.Datetime(
        title=_("Expires"),
        required=False)

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
        default=(),
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

    caption = zope.schema.Text(
        title=_("Image sub text"),
        default=u'',
        required=False)

    links_to = zope.schema.URI(
        title=_('Links to'),
        description=_('Enter a URL this image should link to.'),
        required=False)


class IImage(zeit.cms.interfaces.IAsset,
             zope.app.file.interfaces.IImage):
    """Image."""


class ITransform(zope.interface.Interface):

    def thumbnail(width, height):
        """Create a thumbnail version of the image.

        returns IImage object.
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
