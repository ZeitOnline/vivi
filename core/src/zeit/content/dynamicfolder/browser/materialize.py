from zeit.cms.i18n import MessageFactory as _
import zeit.content.dynamicfolder.materialize
import zeit.cms.browser.menu
import zeit.cms.browser.view


class Materialize(zeit.cms.browser.view.Base):
    """Materialize contents of dynamic folder"""

    def __call__(self):
        # zope.event to materialize the folder?
        zeit.content.dynamicfolder.materialize.materialize_content.delay(
            self.context)
        self.redirect(self.url(self.context, '@@view.html'))
        return ''


class MenuItem(zeit.cms.browser.menu.ActionMenuItem):

    title = _('Materialize dynamic folder')
