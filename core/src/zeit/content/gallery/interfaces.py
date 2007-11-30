# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.schema

import zeit.cms.interfaces
import zeit.cms.content.interfaces

from zeit.cms.i18n import MessageFactory as _


class IGalleryMetadata(zeit.cms.content.interfaces.ICommonMetadata):
    """Cennter page metadata."""

    image_folder = zope.schema.Object(
        zeit.cms.repository.interfaces.IFolder,
        title=_("Image folder"),
        description=_("Folder containing images to display in the gallery."))


class IGallery(IGalleryMetadata,
               zeit.cms.content.interfaces.IXMLContent,
               zope.app.container.interfaces.IReadContainer):
    """An image gallery"""


    def reload_image_folder():
        """Reload the image folder

        Calling this removes entries from the gallery where the referenced
        object does no longer exist and adds entries for new object.

        """


class IGalleryEntry(zope.interface.Interface):
    """One image in the gallery."""

    image = zope.schema.Object(zeit.content.image.interfaces.IImage)
    thumbnail = zope.schema.Object(zeit.content.image.interfaces.IImage)

    title = zope.schema.TextLine(
        title=_('Title'),
        required=False)

    text = zope.schema.Text(
        title=_("Text"))
