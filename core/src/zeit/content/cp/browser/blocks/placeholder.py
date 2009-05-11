# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.view
import zeit.cms.interfaces
import zeit.content.cp.browser.view
import zope.component
import zope.event
import zope.lifecycleevent

class Drop(zeit.content.cp.browser.view.Action):

    def update(self):
        uniqueId = self.request.form['uniqueId']
        switcher = zope.component.getMultiAdapter(
            (self.context.__parent__, self.context, self.request),
            name='type-switcher')
        teaserlist = switcher('teaser')
        teaserlist.insert(0, zeit.cms.interfaces.ICMSContent(uniqueId))
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
            self.context))
        self.signal('before-reload', 'deleted', self.context.__name__)
        self.signal('after-reload', 'added', teaserlist.__name__)


class SwitchType(zeit.content.cp.browser.view.Action):

    def update(self):
        type = self.request.form['type']
        switcher = zope.component.getMultiAdapter(
            (self.context.__parent__, self.context, self.request),
            name='type-switcher')
        new = switcher(type)
        self.signal('before-reload', 'deleted', self.context.__name__)
        self.signal('after-reload', 'added', new.__name__)
        self.signal(None, 'reload',
                    self.context.__name__, self.url(new, 'contents'))
