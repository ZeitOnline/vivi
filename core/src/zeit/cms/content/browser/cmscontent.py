# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: keyword.py 10103 2008-01-16 12:26:27Z zagy $
import zope.component
import zope.cachedescriptors.property

import zeit.cms.browser.interfaces


class DeleteContent(object):

    def __call__(self, *args, **kwargs):
        form = self.request.form
        if form.get('cancel'):
            return self.redirect_to_parent()

        if form.get('delete'):
            return self.delete()

        return super(DeleteContent, self).__call__(*args, **kwargs)

    def delete(self):
        folder = self.context.__parent__
        del folder[self.context.__name__]
        self.redirect_to_parent()

    def redirect_to_parent(self):
        parent = self.context.__parent__
        url = zope.component.getMultiAdapter((parent, self.request),
                                             name='absolute_url')()
        self.request.response.redirect(url)

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
    def uniqueId(self):
        list_repr = zope.component.queryMultiAdapter(
            (self.context, self.request),
            zeit.cms.browser.interfaces.IListRepresentation)
        return list_repr.uniqueId


class RenameContent(object):

    pass
