# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.browser.blocks.block
import zeit.content.cp.interfaces
import zeit.content.image.interfaces
import zope.formlib.form


class Display(object):

    @property
    def image(self):
        if self.context.image:
            image = self.context.image
        else:
            images = zeit.content.image.interfaces.IImages(
                self.context.referenced_object).images
            if images:
                image = images[0]
            else:
                return

        if not zeit.content.image.interfaces.IImageGroup.providedBy(image):
            return image

        image_group = image
        size = self.context.layout
        key = '%s-%s.jpg' % (image_group.__name__, size)
        return image_group[key]


class EditProperties(zeit.content.cp.browser.blocks.block.EditCommon):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IFullGraphicalBlock).omit(
            *list(zeit.content.cp.interfaces.IBlock))
