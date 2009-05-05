# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.view
import zeit.cms.interfaces
import zope.component
import zope.event
import zope.lifecycleevent

class Drop(zeit.cms.browser.view.Base):

    def __call__(self, uniqueId):
        switcher = zope.component.getMultiAdapter(
            (self.context.__parent__, self.context, self.request),
            name='type-switcher')
        teaserlist = switcher('teaser')
        teaserlist.insert(0, zeit.cms.interfaces.ICMSContent(uniqueId))
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
            self.context))


class SwitchType(zeit.cms.browser.view.Base):

    def __call__(self, type):
        switcher = zope.component.getMultiAdapter(
            (self.context.__parent__, self.context, self.request),
            name='type-switcher')
        return self.url(switcher(type))
