import zope.cachedescriptors.property

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.repository.interfaces import IRepositoryContent
from zeit.content.dynamicfolder.interfaces import IMaterializedContent

import zeit.content.dynamicfolder.materialize
import zeit.cms.browser.menu
import zeit.cms.browser.view


class Materialize(zeit.cms.browser.view.Base):
    """Materialize contents of dynamic folder"""

    nextURL = None

    def __call__(self, *args, **kwargs):
        form = self.request.form
        if form.get('form.actions.delete'):
            return self.materialize()
        return super().__call__(*args, **kwargs)

    def materialize(self):
        zeit.content.dynamicfolder.materialize.materialize_content.delay(
            self.context.uniqueId)
        next_url = self.url(self.context, '@@view.html')
        return'<span class="nextURL">%s</span>' % next_url

    @zope.cachedescriptors.property.Lazy
    def container_title(self):
        return self.context.__name__

    @zope.cachedescriptors.property.Lazy
    def content_count(self):
        content = [
            IMaterializedContent.providedBy(self.context[key]) for key in
            self.context.keys()]
        return str(sum(content))

    @zope.cachedescriptors.property.Lazy
    def title(self):
        list_repr = zope.component.queryMultiAdapter(
            (self.context, self.request),
            zeit.cms.browser.interfaces.IListRepresentation)
        return list_repr.title

    @zope.cachedescriptors.property.Lazy
    def unique_id(self):
        return self.context.uniqueId


class MenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):
    """Publish menu item."""

    title = _('Materialize dynamic folder and update content')

    @property
    def visible(self):
        return IRepositoryContent.providedBy(self.context)

    def render(self):
        if self.visible:
            return super().render()
        else:
            return ''
