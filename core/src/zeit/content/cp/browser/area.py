# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.browser.view
import zope.event
import zope.lifecycleevent


class UpdateOrder(zeit.content.cp.browser.view.Action):

    keys = zeit.content.cp.browser.view.Form('keys', json=True)

    def update(self):
        self.context.updateOrder(self.keys)
        zope.event.notify(
            zope.lifecycleevent.ObjectModifiedEvent(self.context))
