# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.cachedescriptors.property
import zope.component

import gocept.fckeditor.connector

import zeit.cms.repository.interfaces
import zeit.cms.clipboard.interfaces
import zeit.cms.browser.interfaces


class FileBrowser(gocept.fckeditor.connector.FCKEditorBrowser):

    @zope.cachedescriptors.property.Lazy
    def fake_root(self):
        return dict((obj.__name__, obj) for obj in (
            self.repository, self.clipboard))

    @zope.cachedescriptors.property.Lazy
    def current_folder(self):
        path = self.request.get('CurrentFolder').strip('/').split('/')
        if len(path) == 1 and not path[0]:
            return self.fake_root
        root = self.fake_root[path[0]]
        remaining_path = '/'.join(path[1:])

        if not remaining_path:
            return root
        return zope.traversing.interfaces.ITraverser(root).traverse(
            remaining_path)

    @zope.cachedescriptors.property.Lazy
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    @zope.cachedescriptors.property.Lazy
    def clipboard(self):
        return zeit.cms.clipboard.interfaces.IClipboard(self.request.principal)

    def _list_folders(self):
        return self.dictify(super(FileBrowser, self)._list_folders())

    def _list_files(self):
        return self.dictify(super(FileBrowser, self)._list_files())

    def dictify(self, objects):
        for obj in objects:
            name = obj.__name__
            list_repr = self.get_list_repr(obj)
            if list_repr is None:
                title = name
                uniqueId = None
                id_and_title = name
            else:
                title = list_repr.title
                unique_id = list_repr.uniqueId
                id_and_title = u'%s (%s)' % (name, title)

            yield dict(
                id=name,
                title=title,
                uniqueId=unique_id,
                id_and_title = id_and_title)

    def get_list_repr(self, obj):
        return zope.component.queryMultiAdapter(
            (obj, self.request),
            zeit.cms.browser.interfaces.IListRepresentation)

