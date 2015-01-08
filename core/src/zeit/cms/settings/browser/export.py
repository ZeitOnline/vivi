
import zope.cachedescriptors.property

import zeit.cms.settings.interfaces


class XML(object):

    @zope.cachedescriptors.property.Lazy
    def settings(self):
        return zeit.cms.settings.interfaces.IGlobalSettings(self.context)
