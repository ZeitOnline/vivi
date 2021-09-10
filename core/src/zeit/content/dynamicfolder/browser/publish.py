from zeit.cms.i18n import MessageFactory as _
import zeit.content.dynamicfolder.publish
import zeit.cms.browser.menu
import zeit.cms.browser.view


class PublishMaterializedContent(zeit.cms.browser.view.Base):
    """Materialize contents of dynamic folder"""

    def __call__(self):
        zeit.content.dynamicfolder.publish.publish_content.delay(
            self.context.uniqueId)
        self.redirect(self.url(self.context, '@@view.html'))
        return ''


class MenuItem(zeit.cms.browser.menu.ActionMenuItem):

    title = _('Publish dynamic folder')
