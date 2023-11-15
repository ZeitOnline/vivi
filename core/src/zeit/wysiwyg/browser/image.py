import zeit.content.image.interfaces
import zeit.cms.browser.view


class Images(zeit.cms.browser.view.JSON):
    def json(self):
        images = zeit.content.image.interfaces.IImages(self.context)
        result = []
        image = images.image
        if image:
            if zeit.content.image.interfaces.IImageGroup.providedBy(image):
                for i in image.values():
                    result.append(i)
            else:
                result.append(image)
        return {'images': [x.uniqueId for x in result]}
