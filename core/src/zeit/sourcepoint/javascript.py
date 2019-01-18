from zope.cachedescriptors.property import Lazy as cachedproperty
import zeit.cms.interfaces
import zeit.sourcepoint.interfaces
import zope.app.appsetup.product
import zope.interface


class JavaScript(object):

    zope.interface.implements(zeit.sourcepoint.interfaces.IJavaScript)

    def __init__(self, folder_id):
        self.folder_id = folder_id

    @cachedproperty
    def folder(self):
        return zeit.cms.interfaces.ICMSContent(self.folder_id)

    @property
    def latest_version(self):
        names = sorted(self.folder.keys(), reverse=True)
        if not names:
            return None
        return self.folder[names[0]]


@zope.interface.implementer(zeit.sourcepoint.interfaces.IJavaScript)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.sourcepoint')
    return JavaScript(config['javascript-folder'])
