from zeit.cms.i18n import MessageFactory as _
import PIL.Image
import zope.interface
import zope.schema


class NotAnImageError(zope.schema.ValidationError):

    __doc__ = _('The uploaded image could not be identified.')


def is_image(value):
    try:
        try:
            PIL.Image.open(value)
        except IOError:
            raise NotAnImageError()
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

    master_image_blobs = zope.schema.Tuple(
        title=_('Upload master images'),
        unique=True,
        required=True,
        min_length=1,
        missing_value=(),
        value_type=zope.schema.Object(
            zope.interface.Interface,
            required=False,
            constraint=is_image))
