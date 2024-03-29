from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.menu
import zeit.cms.checkout


class EditContentsMenuItem(zeit.cms.browser.menu.ContextViewsMenu):
    weight = -1
    viewURL = '@@edit.html'
    activeCSS = 'edit_contents selected'
    inActiveCSS = 'edit_contents'

    @property
    def title(self):
        """Changes wheter item is checked out or checked in"""
        checkout = zeit.cms.checkout.interfaces.ICheckoutManager(self.context)
        if checkout.canCheckout:
            return _('View')
        return _('Edit contents')

    @property
    def selected(self):
        """We are selected when no other item is selected."""
        selected = self.request.getURL().endswith('@@edit.html')
        selected = selected or self.request.getURL().endswith('@@view.html')
        return selected
