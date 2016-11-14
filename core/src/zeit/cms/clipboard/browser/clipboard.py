import transaction
import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.cms.browser.tree
import zeit.cms.clipboard.interfaces
import zeit.cms.interfaces
import zope.cachedescriptors.property
import zope.component
import zope.traversing.api
import zope.traversing.interfaces
import zope.viewlet.viewlet


class Sidebar(zope.viewlet.viewlet.ViewletBase):

    @zope.cachedescriptors.property.Lazy
    def clipboard(self):
        return zeit.cms.clipboard.interfaces.IClipboard(self.request.principal)


class Tree(zeit.cms.browser.tree.Tree):
    """Clipboard tree"""

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

    def getDisplayedUniqueId(self, object):
        if zeit.cms.clipboard.interfaces.IObjectReference.providedBy(object):
            return object.referenced_unique_id
        return None

    def addContent(self, add_to, unique_id):
        container = self.getAddContext(add_to)
        add_object = zeit.cms.interfaces.ICMSContent(unique_id)
        self.context.addContent(container, add_object, add_object.__name__,
                                insert=self.expanded(container))
        return self()

    def addContainer(self, title):
        self.context.addClip(title)
        return self()

    def moveContent(self, add_to, object_path):
        container = self.getAddContext(add_to)
        obj = zope.traversing.interfaces.ITraverser(
            self.context).traverse(object_path)
        try:
            self.context.moveObject(
                obj, container, insert=self.expanded(container))
        except ValueError:
            transaction.doom()
        return self()

    def getTitle(self, obj):
        if zeit.cms.clipboard.interfaces.IClip.providedBy(obj):
            return obj.title
        else:
            list_repr = zope.component.queryMultiAdapter(
                (obj, self.request),
                zeit.cms.browser.interfaces.IListRepresentation)
            if list_repr is not None and list_repr.title:
                return list_repr.title
        return super(Tree, self).getTitle(obj)

    def getType(self, obj):
        if not zeit.cms.clipboard.interfaces.IObjectReference.providedBy(obj):
            return ''

        for interface in zope.interface.providedBy(obj.references):
            try:
                return interface.getTaggedValue('zeit.cms.type')
            except KeyError:
                continue
        return ''

    def getAddContext(self, add_to):
        if add_to:
            return zope.traversing.interfaces.ITraverser(
                self.context).traverse(add_to)
        return self.context

    def selected(self, url):
        return None

    def getDeleteUrl(self, obj):
        url = self.getUrl(obj)
        return url + '/@@ajax-delete-entry'


class ClipboardListRepresentation(
        zeit.cms.browser.listing.BaseListRepresentation):

    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)
    zope.component.adapts(zeit.cms.clipboard.interfaces.IClipboard,
                          zope.publisher.interfaces.IPublicationRequest)

    author = subtitle = byline = ressort = volume = page = year = None

    title = 'Clipboard'
    uniqueId = None

    @zope.cachedescriptors.property.Lazy
    def searchableText(self):
        return self.title
