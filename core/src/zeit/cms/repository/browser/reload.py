# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.event

import zeit.connector.interfaces

import zeit.cms.browser.menu
import zeit.cms.browser.view
from zeit.cms.i18n import MessageFactory as _

class Reload(zeit.cms.browser.view.Base):
    """Reload folder (invalidate cache)."""

    def __call__(self):
        zope.event.notify(
            zeit.connector.interfaces.ResourceInvaliatedEvent(
                self.context.uniqueId))
        self.redirect(self.url(self.context, '@@view.html'))
        return ''


class MenuItem(zeit.cms.browser.menu.ActionMenuItem):
    """Delete menu item."""

    title = _('Reload folder')
