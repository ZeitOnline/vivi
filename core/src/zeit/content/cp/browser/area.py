# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.edit.browser.view
import zope.event
import zope.lifecycleevent


class UpdateOrder(zeit.edit.browser.view.Action):

    keys = zeit.edit.browser.view.Form('keys', json=True)

    def update(self):
        self.context.updateOrder(self.keys)
        zope.event.notify(
            zope.lifecycleevent.ObjectModifiedEvent(self.context))
