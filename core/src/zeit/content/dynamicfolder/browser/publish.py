from zeit.cms.i18n import MessageFactory as _
from zeit.cms.repository.interfaces import IRepositoryContent
from zeit.content.dynamicfolder.interfaces import ICloneArmy

import zeit.cms.browser.menu
import zeit.cms.browser.view
import zeit.content.dynamicfolder.publish


class PublishMaterializedContent(zeit.cms.browser.view.Base):

    def __call__(self):
        zeit.content.dynamicfolder.publish.publish_content.delay(
            self.context.uniqueId)
        self.redirect(self.url(self.context, '@@view.html'))
        return ''


class MenuItem(zeit.cms.browser.menu.ActionMenuItem):

    title = _('Publish content of dynamic folder')

    @property
    def visible(self):
        return IRepositoryContent.providedBy(self.context)

    def render(self):
        if ICloneArmy(self.context).activate and self.visible:
            return super().render()
        else:
            return ''
