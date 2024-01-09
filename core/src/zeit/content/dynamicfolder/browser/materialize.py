import zope.cachedescriptors.property

from zeit.cms.i18n import MessageFactory as _
from zeit.content.dynamicfolder.interfaces import ICloneArmy, IMaterializedContent
import zeit.cms.browser.menu
import zeit.cms.browser.view
import zeit.content.dynamicfolder.materialize


class Materialize(zeit.cms.browser.view.Base):
    """Materialize contents of dynamic folder"""

    nextURL = None

    def __call__(self):
        form = self.request.form
        if form.get('form.actions.delete'):
            return self.materialize()
        return super().__call__()

    def materialize(self):
        zeit.content.dynamicfolder.materialize.materialize_content(self.context)
        next_url = self.url(self.context, '@@view.html')
        return '<span class="nextURL">%s</span>' % next_url

    @zope.cachedescriptors.property.Lazy
    def container_title(self):
        return self.context.__name__

    @zope.cachedescriptors.property.Lazy
    def content_count(self):
        content = [IMaterializedContent.providedBy(val) for val in self.context.values()]
        return str(sum(content))


class CloneArmyGuard:
    @property
    def visible(self):
        return ICloneArmy(self.context).activate

    def render(self):
        if self.visible:
            return super().render()
        else:
            return ''


class MaterializeMenuItem(CloneArmyGuard, zeit.cms.browser.menu.LightboxActionMenuItem):
    title = _('Materialize dynamic folder and update content')


class PublishMaterializedContent(zeit.cms.browser.view.Base):
    def __call__(self):
        zeit.content.dynamicfolder.materialize.publish_content(self.context)
        self.redirect(self.url(self.context, '@@view.html'))
        return ''


class PublishMenuItem(CloneArmyGuard, zeit.cms.browser.menu.ActionMenuItem):
    title = _('Publish content of dynamic folder')
