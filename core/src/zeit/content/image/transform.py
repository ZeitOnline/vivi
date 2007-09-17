# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import cStringIO

import Image  # PIL

import zope.component
import zope.interface

import zeit.content.image.interfaces


class ImageTransform(object):

    zope.interface.implements(zeit.content.image.interfaces.ITransform)
    zope.component.adapts(zeit.content.image.interfaces.IImage)

    def __init__(self, context):
        self.context = context
        try:
            self.image = Image.open(cStringIO.StringIO(context.data))
            self.image.load()
        except IOError:
            raise TypeError("Cannot transform image %s (%s)" % (
                context, context.contentType))

    def thumbnail(self, width, height):
        self.image.thumbnail((width, height), Image.ANTIALIAS)

        image_data = cStringIO.StringIO()
        self.image.save(image_data, self.image.format)

        image = zeit.content.image.image.Image(data=image_data.getvalue())
        image.__parent__ = self.context
        return image
