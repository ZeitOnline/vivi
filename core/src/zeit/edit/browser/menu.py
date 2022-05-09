from zeit.cms.i18n import MessageFactory as _
from zeit.cms.repository.interfaces import IRepositoryContent
import zeit.cms.browser.menu


class EditContentsMenuItem(zeit.cms.browser.menu.ContextViewsMenu):

    sort = -1
    viewURL = "@@edit.html"
    title = _("Edit contents")
    activeCSS = 'edit_contents selected'
    inActiveCSS = 'edit_contents'

    @property
    def selected(self):
        selected = self.request.getURL().endswith('@@edit.html')
        return selected

    def render(self):
        if IRepositoryContent.providedBy(self.context):
            return ''
        return super().render()
