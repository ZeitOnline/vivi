# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import transaction

import zope.component
import zope.cachedescriptors.property
import zope.viewlet.viewlet
import zope.traversing.interfaces
import zope.traversing.api

import zeit.cms.browser.interfaces
import zeit.cms.browser.tree
import zeit.cms.repository.interfaces
import zeit.cms.browser.listing

import zeit.cms.clipboard.interfaces


class Sidebar(zope.viewlet.viewlet.ViewletBase):

    @zope.cachedescriptors.property.Lazy
    def clipboard(self):
        return zeit.cms.clipboard.interfaces.IClipboard(self.request.principal)


class Tree(zeit.cms.browser.tree.Tree):
    """Clipbaord tree"""

    root_name = 'Clipboard'
    key = __module__ + '.Tree'

    @zope.cachedescriptors.property.Lazy
    def root(self):
        """repository representing the root of the tree"""
        return zeit.cms.clipboard.interfaces.IClipboard(self.request.principal)

    def isRoot(self, container):
        return zeit.cms.clipboard.interfaces.IClipboard.providedBy(container)

    def getUniqueId(self, object):
        if self.isRoot(object):
            return ''
        root_path = zope.traversing.api.getPath(self.root)
        full_path = zope.traversing.api.getPath(object)
        relative = full_path[len(root_path) + 1:]
        return relative

    def addContent(self, add_to, unique_id):
        container = self.getAddContext(add_to)
        add_object = self.repository.getContent(unique_id)
        self.context.addContent(container, add_object, add_object.__name__)
        return self()

    def addContainer(self, title):
        self.context.addClip(title)
        return self()

    def moveContent(self, add_to, object_path):
        container = self.getAddContext(add_to)
        obj = zope.traversing.interfaces.ITraverser(
            self.context).traverse(object_path)
        try:
            self.context.moveObject(obj, container)
        except ValueError:
            transaction.abort()
        return self()

    @zope.cachedescriptors.property.Lazy
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    def getObjectData(self, obj):
        data = super(Tree, self).getObjectData(obj)
        if zeit.cms.clipboard.interfaces.IClip.providedBy(obj):
            data['title'] = obj.title
        else:
            list_repr = zope.component.queryMultiAdapter(
                (obj, self.request),
                zeit.cms.browser.interfaces.IListRepresentation)
            if list_repr is not None and list_repr.title:
                data['title'] = list_repr.title
        return data

    def getAddContext(self, add_to):
        if add_to:
            return zope.traversing.interfaces.ITraverser(
                self.context).traverse(add_to)
        return self.context

    def selected(self, url):
        return None


class ClipboardListRepresentation(
    zeit.cms.browser.listing.BaseListRepresentation):

    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)
    zope.component.adapts(zeit.cms.clipboard.interfaces.IClipboard,
                          zope.publisher.interfaces.IPublicationRequest)

    author = subtitle = byline = ressort = volume = page = year = None

    title = 'Clipboard'

    @zope.cachedescriptors.property.Lazy
    def searchableText(self):
        return self.title
