import zeit.cms.browser.menu
import zeit.cms.checkout.interfaces
import zeit.cms.workflow.interfaces


class MenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):

    weight = -1
    lightbox = '@@publish.html'

    def is_visible(self):
        manager = zeit.cms.checkout.interfaces.ICheckinManager(self.context)
        return manager.canCheckin

    # XXX duplicated from zeit.cms.checkout.browser.MenuItem
    def render(self):
        if self.is_visible():
            return super().render()
        return ''
