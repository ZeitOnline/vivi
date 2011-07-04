# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.edit.browser.view
import zope.event
import zope.lifecycleevent


class UpdateOrder(zeit.edit.browser.view.Action):

    keys = zeit.edit.browser.view.Form('keys', json=True)

    def update(self):
        self.undo_description = _('change block order')
        self.context.updateOrder(self.keys)
        zope.event.notify(
            zope.lifecycleevent.ObjectModifiedEvent(self.context))


class Move(zeit.edit.browser.view.Action):

    key = zeit.edit.browser.view.Form('key')

    def update(self):
        self.undo_description = _('change block order')

        # XXX this assumes a simple, non-nested structure, is that general
        # enough?
        for container in self.context.__parent__.values():
            if self.key in container:
                item = container[self.key]
                del container[self.key]
                break
        else:
            raise KeyError(self.key)

        self.context.add(item)
