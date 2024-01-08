from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.menu


class Global(zeit.cms.browser.menu.GlobalMenuItem):
    """Global settings menu item."""

    title = _('Global settings')
    viewURL = '@@global-settings.html'
    pathitem = '@@global-settings.html'
