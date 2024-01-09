import zope.event

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.menu
import zeit.cms.browser.view
import zeit.cms.repository.interfaces
import zeit.connector.interfaces


class Reload(zeit.cms.browser.view.Base):
    """Reload folder (invalidate cache)."""

    def __call__(self):
        zope.event.notify(zeit.connector.interfaces.ResourceInvaliatedEvent(self.context.uniqueId))
        zope.event.notify(zeit.cms.repository.interfaces.ObjectReloadedEvent(self.context))
        self.redirect(self.url(self.context, '@@view.html'))
        return ''


class MenuItem(zeit.cms.browser.menu.ActionMenuItem):
    """Delete menu item."""

    title = _('Reload folder')
