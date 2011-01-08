# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import os

import BTrees.OOBTree

import zope.annotation.factory
import zope.security.interfaces
import zope.publisher.browser

import zope.app.pagetemplate

import zc.set

import zeit.cms.browser.interfaces


class TreeState(BTrees.OOBTree.OOBTree):

    zope.component.adapts(zope.security.interfaces.IPrincipal)
    zope.interface.implements(zeit.cms.browser.interfaces.ITreeState)


treeStateFactory = zope.annotation.factory(TreeState)


class Tree(zope.publisher.browser.BrowserView):
    """Abstract base class for rendering trees."""

    zope.interface.implements(zeit.cms.browser.interfaces.ITree)

    # Subclasses need to define root and a key for the treestate
    root = None
    key = None

    tree_template = zope.app.pagetemplate.ViewPageTemplateFile('tree.pt')

    def __call__(self):
        return self.tree_template()

    def getTreeData(self):
        result = self.getSubTree([self.root])
        return result

    def getSubTree(self, objects):
        data = []

        for obj in objects:
            container_data = self.getObjectData(obj)

            if container_data['expanded']:
                sub_data = self.getSubTree(self.listContainer(obj))
            else:
                sub_data = []

            container_data['sub_data'] = sub_data
            data.append(container_data)
        return data

    def listContainer(self, container):
        for obj in container.values():
            yield obj

    def getObjectData(self, obj):
        url = self.getUrl(obj)
        expandable = self.expandable(obj)
        uid = self.getUniqueId(obj)

        root = False
        if self.isRoot(obj):
            root = True

        expanded = self.expanded(obj)

        if not root and expandable:
            action = expanded and 'collapse' or 'expand'
        else:
            action = None

        selected = self.selected(url)
        if not selected:
            selected = None

        return {'title': self.getTitle(obj),
                'id': self.getId(obj),
                'action': action,
                'uniqueId': uid,
                'displayedObjectUniqueId': self.getDisplayedUniqueId(obj),
                'expanded': expanded,
                'subfolders': expandable,
                'isroot': root,
                'url': url,
                'delete_url': self.getDeleteUrl(obj),
                'selected': selected}

    def getTitle(self, obj):
        if self.isRoot(obj):
            return self.root_name
        return self.getId(obj)

    def getId(self, obj):
        return obj.__name__

    def getUrl(self, obj):
        """Returns the absolute url of obj"""
        return zope.component.getMultiAdapter(
            (obj, self.request),
            name='absolute_url')()

    def getDeleteUrl(self, obj):
        """Returns the url to delete this content item."""
        return ''

    def expandable(self, obj):
        """Returns if the obj can be expanded or collapsed.

        So in general, if it is a container, and it contains items, it is
        expandable.

        """
        if zope.app.container.interfaces.IContainer.providedBy(obj):
            return True
        return False

    def expanded(self, obj):
        if self.isRoot(obj):
            return True
        return self.getUniqueId(obj) in self.treeState

    @property
    def treeState(self):
        key = self.key
        if key is None:
            raise NotImplementedError("No `key` set.")
        tree_states = zeit.cms.browser.interfaces.ITreeState(
            self.request.principal)
        try:
            state = tree_states[key]
        except KeyError:
            tree_states[key] = state = zc.set.Set()
        return state

    def isRoot(self, container):
        raise NotImplementedError

    def getUniqueId(self, object):
        raise NotImplementedError

    def getDisplayedUniqueId(self, object):
        return self.getUniqueId(object)

    def selected(self, url):
        raise NotImplementedError

    def expandNode(self, uniqueId):
        self.treeState.add(uniqueId)

    def collapseNode(self, uniqueId):
        try:
            self.treeState.remove(uniqueId)
        except KeyError:
            # If unique id is not in the state it is already collapsed. That's
            # okay
            pass


class TreeExpand(object):

    def __call__(self, uniqueId):
        self.context.expandNode(uniqueId)
        return self.context()


class TreeCollapse(object):

    def __call__(self, uniqueId):
        self.context.collapseNode(uniqueId)
        return self.context()
