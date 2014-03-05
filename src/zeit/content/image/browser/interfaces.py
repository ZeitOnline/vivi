# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import PIL.Image
import zope.component
import zope.interface
import zope.schema


class NotAnImageError(zope.schema.ValidationError):

    def doc(self):
        return _('The uploaded image could not be identified.')


def is_image(value):
    try:
        try:
            PIL.Image.open(value)
        except IOError:
            raise NotAnImageError
    finally:
        value.seek(0)
    return True


class IFileAddSchema(zope.interface.Interface):

    __name__ = zope.schema.TextLine(
        title=_('File name'),
        required=False)

    blob = zope.schema.Object(
        zope.interface.Interface,
        title=_('Upload new image'),
        required=True,
        constraint=is_image)


class IFileEditSchema(IFileAddSchema):

    blob = zope.schema.Object(
        zope.interface.Interface,
        title=_('Upload new image'),
        required=False,
        constraint=is_image)


class IMasterImageUploadSchema(zope.interface.Interface):

    blob = zope.schema.Object(
        zope.interface.Interface,
        title=_('Upload master image'),
        description=_('upload-master-image-description'),
        required=False,
        constraint=is_image)
