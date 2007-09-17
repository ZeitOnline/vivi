# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component

import zeit.content.image.interfaces


class ImageBrowser(object):

    def images(self):
        for obj in self.context.values():
            if not zeit.content.image.interfaces.IImage.providedBy(obj):
                continue
            yield obj
