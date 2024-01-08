import z3c.traverser.interfaces
import zope.annotation
import zope.component
import zope.container.contained
import zope.container.interfaces
import zope.container.ordered
import zope.interface
import zope.proxy
import zope.publisher.interfaces
import zope.security.interfaces
import zope.traversing.api

import zeit.cms.clipboard.interfaces
import zeit.cms.workingcopy.interfaces


@zope.component.adapter(zeit.cms.workingcopy.interfaces.IWorkingcopy)
@zope.interface.implementer(zeit.cms.clipboard.interfaces.IClipboard)
class Clipboard(zope.container.ordered.OrderedContainer):
    title = 'Clipboard'

    def addContent(self, reference_object, add_object, name=None, insert=False):
        """Add unique_id to obj."""
        if not zeit.cms.clipboard.interfaces.IClipboardEntry.providedBy(reference_object):
            raise ValueError(
                '`reference_object` does not provide IClipboardEntry (%r)' % reference_object
            )
        if insert:
            container = reference_object
            position = 0
        else:
            container = reference_object.__parent__
            position = list(container.keys()).index(reference_object.__name__) + 1

        if not zope.container.interfaces.IOrderedContainer.providedBy(container):
            raise ValueError('`reference_object` must be a Clip to insert.')

        entry = zeit.cms.clipboard.interfaces.IClipboardEntry(add_object)
        entry = zope.proxy.removeAllProxies(entry)
        order = list(container.keys())
        chooser = zope.container.interfaces.INameChooser(container)
        name = chooser.chooseName(name, entry)
        container[name] = entry

        order.insert(position, name)
        container.updateOrder(order)

    def addClip(self, title):
        clip = zeit.cms.clipboard.entry.Clip(title)
        chooser = zope.container.interfaces.INameChooser(self)
        name = chooser.chooseName(title, clip)
        self[name] = clip
        return self[name]

    def moveObject(self, obj, new_container, insert=False):
        if not zeit.cms.clipboard.interfaces.IClipboardEntry.providedBy(obj):
            raise TypeError('obj must provided IClipboardEntry. Got %r.' % obj)
        if obj == new_container:
            return
        if obj in zope.traversing.api.getParents(new_container):
            raise ValueError('`obj` must not be an ancestor of `new_container`.')
        old_container = obj.__parent__
        old_name = obj.__name__
        del old_container[old_name]
        self.addContent(new_container, obj, old_name, insert)

    def __setitem__(self, key, value):
        if not zeit.cms.clipboard.interfaces.IClipboardEntry.providedBy(value):
            raise ValueError('Can only contain IClipboardEntry objects. ' 'Got %r instead.' % value)
        super().__setitem__(key, value)


clipboardFactory = zope.annotation.factory(Clipboard)


@zope.interface.implementer(zeit.cms.clipboard.interfaces.IClipboard)
@zope.component.adapter(zope.security.interfaces.IPrincipal)
def principalAdapter(principal):
    """Shortcut adapter from principal to clipboard."""
    workingcopy = zeit.cms.workingcopy.interfaces.IWorkingcopy(principal)
    return zeit.cms.clipboard.interfaces.IClipboard(workingcopy)


@zope.component.adapter(
    zeit.cms.workingcopy.interfaces.IWorkingcopy, zope.publisher.interfaces.IPublisherRequest
)
@zope.interface.implementer(z3c.traverser.interfaces.IPluggableTraverser)
class WorkingcopyTraverser:
    """Traverses to clipboard through a workingcopy."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        clipboard = zeit.cms.clipboard.interfaces.IClipboard(self.context, None)
        if clipboard is not None and clipboard.__name__ == name:
            return clipboard
        raise zope.publisher.interfaces.NotFound(self.context, name, request)


@zope.component.adapter(zeit.cms.clipboard.interfaces.IClipboard)
class ClipboardNameChooser(zope.container.contained.NameChooser):
    """A namechooser removing invalid characters."""

    def chooseName(self, name, object):
        name = name.replace('/', '')
        while name.startswith('+'):
            name = name.replace('+', '', 1)
        while name.startswith('@'):
            name = name.replace('@', '', 1)
        return super().chooseName(name, object)
