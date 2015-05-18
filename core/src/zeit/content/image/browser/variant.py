import zeit.cms.browser.view
import zeit.content.image.interfaces
import zeit.imp.browser.interfaces
import zope.cachedescriptors.property


class Variant(zeit.cms.browser.view.Base):

    @zope.cachedescriptors.property.Lazy
    def image(self):
        try:
            return zeit.content.image.interfaces.IMasterImage(self.context)
        except TypeError:
            raise zeit.imp.browser.interfaces.NoMasterImageError()
