# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.annotation
import zope.component
import zope.interface
import zope.proxy
import zope.publisher.interfaces
import zope.security.interfaces
import zope.traversing.api

import zope.app.container.interfaces
import zope.app.container.ordered

import z3c.traverser.interfaces

import zeit.cms.workingcopy.interfaces
import zeit.cms.clipboard.interfaces


class Clipboard(zope.app.container.ordered.OrderedContainer):

    zope.interface.implements(zeit.cms.clipboard.interfaces.IClipboard)
    zope.component.adapts(zeit.cms.workingcopy.interfaces.IWorkingcopy)

    title = 'Clipboard'

    def addContent(self, reference_object, add_object, name=None):
        """Add unique_id to obj."""
        if zeit.cms.clipboard.interfaces.IClip.providedBy(
            reference_object):
            container = reference_object
            position = 0
        elif zeit.cms.clipboard.interfaces.IClipboardEntry.providedBy(
            reference_object):
            container = reference_object.__parent__
            position = list(container.keys()).index(
                reference_object.__name__) + 1
        else:
            raise ValueError(
                "`reference_object` does not provide IClipboardEntry (%r)" %
                reference_object)

        assert(zope.app.container.interfaces.IOrderedContainer.providedBy(
            container))

        entry = zeit.cms.clipboard.interfaces.IClipboardEntry(add_object)
        entry = zope.proxy.removeAllProxies(entry)
        order = list(container.keys())
        chooser = zope.app.container.interfaces.INameChooser(container)
        name = chooser.chooseName(name, entry)
        container[name] = entry

        order.insert(position, name)
        container.updateOrder(order)

    def addClip(self, title):
        clip = zeit.cms.clipboard.entry.Clip(title)
        chooser = zope.app.container.interfaces.INameChooser(self)
        name = chooser.chooseName(title, clip)
        self[name] = clip

    def moveObject(self, obj, new_container):
        if not zeit.cms.clipboard.interfaces.IClipboardEntry.providedBy(obj):
            raise TypeError("obj must provided IClipboardEntry. Got %r." % obj)
        if obj == new_container:
            return
        if obj in zope.traversing.api.getParents(new_container):
            raise ValueError(
                "`obj` must not be an ancestor of `new_container`.")
        old_container = obj.__parent__
        old_name = obj.__name__
        del old_container[old_name]
        self.addContent(new_container, obj, old_name)

    def __setitem__(self, key, value):
        if not zeit.cms.clipboard.interfaces.IClipboardEntry.providedBy(value):
            raise ValueError("Can only contain IClipboardEntry objects. "
                             "Got %r instead." % value)
        super(Clipboard, self).__setitem__(key, value)


clipboardFactory = zope.annotation.factory(Clipboard)


@zope.interface.implementer(zeit.cms.clipboard.interfaces.IClipboard)
@zope.component.adapter(zope.security.interfaces.IPrincipal)
def principalAdapter(principal):
    """Shortcut adapter from principal to clipboard."""
    workingcopy = zeit.cms.workingcopy.interfaces.IWorkingcopy(principal)
    return zeit.cms.clipboard.interfaces.IClipboard(workingcopy)


class WorkingcopyTraverser(object):
    """Traverses to clipboard through a workingcopy."""

    zope.interface.implements(z3c.traverser.interfaces.IPluggableTraverser)
    zope.component.adapts(
        zeit.cms.workingcopy.interfaces.IWorkingcopy,
        zope.publisher.interfaces.IPublisherRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        clipboard = zeit.cms.clipboard.interfaces.IClipboard(
            self.context, None)
        if clipboard is not None and clipboard.__name__ == name:
            return clipboard
        raise zope.publisher.interfaces.NotFound(self.context, name, request)
