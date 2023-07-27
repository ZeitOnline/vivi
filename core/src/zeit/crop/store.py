import zeit.content.image.image
import zeit.content.image.interfaces
import zeit.crop.interfaces
import zope.component
import zope.interface


@zope.component.adapter(zeit.content.image.interfaces.IRepositoryImageGroup)
@zope.interface.implementer(zeit.crop.interfaces.IStorer)
class ImageGroupStorer:

    def __init__(self, context):
        self.context = self.__parent__ = context

    def store(self, name, pil_image):
        image = zeit.content.image.image.LocalImage()
        image_format = zeit.content.image.interfaces.IMasterImage(
            self.context).format
        # Luckily, PIL simply ignores kwargs that are not supported by a
        # format, so we can always specify quality, even though it only makes
        # sense for JPEG, but not PNG.
        with image.open('w') as f:
            pil_image.save(f, image_format, optimize=True, quality=80)
        extension = image_format.lower()
        # XXX Ugly heuristic, but using .jpg is not only generally nicer, but
        # also backwards-compatible behaviour.
        if extension == 'jpeg':
            extension = 'jpg'
        image_name = '%s-%s.%s' % (self.context.__name__, name, extension)
        self.context[image_name] = image

        return image
