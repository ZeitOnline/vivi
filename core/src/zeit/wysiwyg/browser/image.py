# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.image.interfaces
import zeit.cms.browser.view


class Images(zeit.cms.browser.view.JSON):

    def json(self):
        images = zeit.content.image.interfaces.IImages(self.context)
        result = []
        for image in images.images:
            if zeit.content.image.interfaces.IImageGroup.providedBy(image):
                for i in image.values():
                    result.append(i)
            else:
                result.append(image)
        return dict(
            images=[image.uniqueId for image in result])
