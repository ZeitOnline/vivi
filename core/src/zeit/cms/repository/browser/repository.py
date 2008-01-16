# Copyright (c) 2007-2008 gocept gmbh & co. kg
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
        for obj in container.values():
            if not zeit.cms.repository.interfaces.ICollection.providedBy(obj):
                continue
            if self.preferences.is_hidden(obj):
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
        self.preferences.hide_container(self.context)

    def remove_from_preference(self):
        self.preferences.show_container(self.context)

    @property
    def hidden(self):
        return self.preferences.is_hidden(self.context)

    @zope.cachedescriptors.property.Lazy
    def preferences(self):
        return zeit.cms.repository.interfaces.IUserPreferences(
            zeit.cms.workingcopy.interfaces.IWorkingcopy(
                self.request.principal))
