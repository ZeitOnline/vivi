# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.tree
import zeit.cms.repository.interfaces
import zope.component


class Tree(zeit.cms.browser.tree.Tree):

    root_name = _('Start')
    key = __module__ + '.Tree'

    @zope.cachedescriptors.property.Lazy
    def root(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    def isRoot(self, container):
        return zeit.cms.repository.interfaces.IRepository.providedBy(
            container)

    def listContainer(self, container):
        if self.isRoot(container):
            source = zeit.cms.content.sources.NavigationSource()
        else:
            source = zeit.cms.content.sources.SubNavigationSource()(container)
        names = list(source)
        return [container[x.lower()] for x in names if x.lower() in container]

    def getTitle(self, obj):
        return super(Tree, self).getTitle(obj).title()

    def getUniqueId(self, object):
        if self.isRoot(object):
            return None
        return object.uniqueId

    def getUrl(self, obj):
        return super(Tree, self).getUrl(obj) + '/index/@@checkout'

    def selected(self, url):
        return False

    def expandable(self, obj):
        return self.isRoot(obj.__parent__) or self.isRoot(obj)
