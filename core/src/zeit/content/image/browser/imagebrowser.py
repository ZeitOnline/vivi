from zeit.cms.i18n import MessageFactory as _
import zeit.content.image.interfaces


class ImageBrowser:

    title = _("Images")

    def images(self):
        for obj in self.context.values():
            if not zeit.content.image.interfaces.IImage.providedBy(obj):
                continue
            metadata = zeit.content.image.interfaces.IImageMetadata(obj)
            yield dict(
                image=obj,
                metadata=metadata)
