# vim: fileencoding=utf8 encoding=utf8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.schema

import zope.app.file.interfaces

import zeit.cms.interfaces


class IImageType(zeit.cms.interfaces.ICMSContentType):
    """The interface of image interfaces."""


class IImageSchema(zope.app.file.interfaces.IImage):

    expires = zope.schema.Datetime(
        title=u"Löschdatum",
        required=False)

    title = zope.schema.TextLine(
        title=u"Bildtitel",
        default=u'',
        required=False)

    year = zope.schema.Int(
        title=u"Jahr",
        min=1900,
        max=2100,
        required=False)

    volume = zope.schema.Int(
        title=u"Ausgabe",
        min=1,
        max=53,
        required=False)

    copyrights = zope.schema.TextLine(
        title=u"copyright ©",
        description=u"© nicht eintippen.",
        default=u"ZEIT online",
        required=False)

    alt = zope.schema.TextLine(
        title=u"ALT-Text",
        default=u'',
        required=False)

    caption = zope.schema.Text(
        title=u"Bildunterschrift",
        default=u'',
        required=False)


class IImage(zeit.cms.interfaces.ICMSContent,
             IImageSchema):
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


class IImageGroup(zope.app.container.interfaces.IContainer,
                  zeit.cms.interfaces.ICMSContent):
    """An image group groups images with the same motif together."""
