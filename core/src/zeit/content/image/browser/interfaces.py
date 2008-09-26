# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import PIL.Image

import zope.interface
import zope.schema

from zeit.cms.i18n import MessageFactory as _

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


class IFileEditSchema(zope.interface.Interface):

    __name__ = zope.schema.TextLine(
        title=_('File name'),
        required=False)

    blob = zope.schema.Object(
        zope.interface.Interface,
        title=_('Upload new image'),
        required=False,
        constraint=is_image)
