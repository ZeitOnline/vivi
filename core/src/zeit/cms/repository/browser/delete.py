# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
"""Delete content."""

import zope.component
import zope.cachedescriptors.property

import zeit.cms.browser.view
import zeit.cms.browser.interfaces
import zeit.cms.repository.interfaces


class DeleteContent(zeit.cms.browser.view.Base):

    nextURL = None

    def __call__(self, *args, **kwargs):
        form = self.request.form
        if form.get('form.actions.delete'):
            return self.delete()
        return super(DeleteContent, self).__call__(*args, **kwargs)

    def next_url(self, folder):
        return self.url(folder)

    def delete(self):
        folder = self.context.__parent__
        self._delete()
        next_url = self.next_url(folder)
        return '<span class="nextURL">%s</span>' % next_url

    def _delete(self):
        folder = self.context.__parent__
        del folder[self.context.__name__]

    @zope.cachedescriptors.property.Lazy
    def container_title(self):
        return self.context.__parent__.__name__

    @zope.cachedescriptors.property.Lazy
    def title(self):
        list_repr = zope.component.queryMultiAdapter(
            (self.context, self.request),
            zeit.cms.browser.interfaces.IListRepresentation)
        return list_repr.title

    @zope.cachedescriptors.property.Lazy
    def icon(self):
        icon = zope.component.queryMultiAdapter(
            (self.context, self.request), name="zmi_icon")
        if icon:
            return icon()

    @zope.cachedescriptors.property.Lazy
    def unique_id(self):
        return self.context.uniqueId

    @zope.cachedescriptors.property.Lazy
    def is_folder_with_content(self):
        if zeit.cms.repository.interfaces.ICollection.providedBy(self.context):
            return len(self.context) > 1
        return False
