# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt
"""Settings export."""

import zope.cachedescriptors.property

import zeit.cms.settings.interfaces


class XML(object):

    @zope.cachedescriptors.property.Lazy
    def settings(self):
        return zeit.cms.settings.interfaces.IGlobalSettings(self.context)
