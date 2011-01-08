# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component

import zeit.content.image.interfaces
from zeit.cms.i18n import MessageFactory as _

class ImageBrowser(object):

    title = _("Images")

    def images(self):
        for obj in self.context.values():
            if not zeit.content.image.interfaces.IImage.providedBy(obj):
                continue
            metadata = zeit.content.image.interfaces.IImageMetadata(obj)
            yield dict(
                image=obj,
                metadata=metadata)
