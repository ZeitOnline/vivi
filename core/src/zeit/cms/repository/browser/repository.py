# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.cachedescriptors.property
import zope.component
import zope.formlib.form
import zope.viewlet.viewlet

import zeit.cms.browser.form
import zeit.cms.browser.tree
import zeit.cms.interfaces
import zeit.cms.workingcopy.interfaces

import zeit.cms.repository.interfaces
import zeit.cms.repository.repository
from zeit.cms.i18n import MessageFactory as _


class Repository(object):

    def __call__(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)


class HTMLTree(zope.viewlet.viewlet.ViewletBase):
    """view class for navtree"""

    def render(self):
        return self.index()

    @zope.cachedescriptors.property.Lazy
    def repository(self):
        """repository representing the root of the tree"""
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)


class Tree(zeit.cms.browser.tree.Tree):
    """Repository Tree"""

    root_name = 'Repository'
    key = __module__ + '.Tree'

    def listContainer(self, container):
        hidden = self.preferences.hidden_containers
        for obj in container.values():
            if not zeit.cms.repository.interfaces.ICollection.providedBy(obj):
                continue
            if obj in hidden:
                continue
            yield obj

    @zope.cachedescriptors.property.Lazy
    def root(self):
        """repository representing the root of the tree"""
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    def isRoot(self, container):
        return zeit.cms.repository.interfaces.IRepository.providedBy(container)

    def getUniqueId(self, object):
        if self.isRoot(object):
            return None
        return object.uniqueId

    def expanded(self, obj):
        url = self.getUrl(obj)
        if self.selected(url):
            return True
        return super(Tree, self).expanded(obj)

    def selected(self, url):
        view_url = self.request.get('view_url')
        if not view_url:
            view_url = str(self.request.URL)
        return view_url.startswith(url) or None

    @zope.cachedescriptors.property.Lazy
    def preferences(self):
        return zeit.cms.repository.interfaces.IUserPreferences(
            zeit.cms.workingcopy.interfaces.IWorkingcopy(
                self.request.principal))


class HiddenCollections(object):

    def hide_collection(self):
        self.add_to_preference()
        return self.redirect()

    def show_collection(self):
        self.remove_from_preference()
        return self.redirect()

    def redirect(self):
        url = zope.component.getMultiAdapter(
            (self.context, self.request),
            name='absolute_url')()
        self.request.response.redirect(url)
        return ''

    def add_to_preference(self):
        if not self.hidden:
            self.preferences.hidden_containers += (self.context, )

    def remove_from_preference(self):
        if self.hidden:
            # XXX refactor hidden to a frozenset
            hidden = list(self.preferences.hidden_containers)
            hidden.remove(self.context)
            self.preferences.hidden_containers = tuple(hidden)

    @property
    def hidden(self):
        return self.context in self.preferences.hidden_containers

    @zope.cachedescriptors.property.Lazy
    def preferences(self):
        return zeit.cms.repository.interfaces.IUserPreferences(
            zeit.cms.workingcopy.interfaces.IWorkingcopy(
                self.request.principal))


class FolderAdd(zeit.cms.browser.form.AddForm):

    form_fields = zope.formlib.form.Fields(
        zeit.cms.repository.interfaces.IFolder).omit('uniqueId')
    title = _("Add folder")
    widget_groups = (
        (_('Folder'), zeit.cms.browser.form.REMAINING_FIELDS, ''),)

    def create(self, data):
        return zeit.cms.repository.repository.Folder(**data)


class FolderEdit(object):

    title = _("Edit folder")

    def __call__(self):
        url = zope.component.getMultiAdapter(
            (self.context, self.request), name='absolute_url')()
        self.request.response.redirect(url)
        return ''
