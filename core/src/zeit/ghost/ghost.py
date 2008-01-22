# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.dublincore.interfaces
import zope.interface

import zeit.cms.interfaces
import zeit.cms.checkout.interfaces
import zeit.cms.clipboard.entry
import zeit.cms.clipboard.interfaces
import zeit.cms.workingcopy.interfaces


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.ICheckinEvent)
def add_ghost_after_checkin(context, event):
    """Add a ghost for the checked in object."""
    workingcopy = zeit.cms.workingcopy.interfaces.IWorkingcopy(
        event.principal)
    entry = zeit.cms.clipboard.entry.Entry(context)
    zope.interface.directlyProvides(
        entry, zeit.cms.workingcopy.interfaces.ILocalContent)
    chooser = zope.app.container.interfaces.INameChooser(workingcopy)
    name = chooser.chooseName(context.__name__, entry)
    workingcopy[name] = entry


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.ICheckoutEvent)
def remove_ghost_after_checkout(context, event):
    """Remove ghost of checked out object, if any."""
    workingcopy = zeit.cms.workingcopy.interfaces.IWorkingcopy(
        event.principal)
    unique_id = context.uniqueId

    for name in list(workingcopy):
        # Make a list before iterating because the loop is modifying the
        # workingcopy
        content = workingcopy[name]
        if not zeit.cms.clipboard.interfaces.IObjectReference.providedBy(
            content):
            continue
        referenced = content.references
        if referenced is None or unique_id == content.references.uniqueId:
            del workingcopy[name]


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.ICheckoutEvent)
def remove_excessive_ghosts(context, event):
    """Remove ghosts from workingcopy which exceed the target of 7

    Removes ghosts until either the size of the wc is 7 or no ghosts are left
    to remove.

    """
    workingcopy = zeit.cms.workingcopy.interfaces.IWorkingcopy(
        event.principal)
    target_size = 7
    while True:
        if len(workingcopy) <= target_size:
            break
        ghost_removed = remove_oldest_ghost(workingcopy)
        if ghost_removed is None:
            # no ghosts left to remove
            break


def remove_oldest_ghost(workingcopy):
    """Remove the oldest ghost in the workingcopy, if any."""
    ghosts = [
        content for content in workingcopy.values()
        if zeit.cms.clipboard.interfaces.IObjectReference.providedBy(content)]
    if not ghosts:
        return

    ghosts.sort(cmp=lambda x, y: cmp(
        zope.dublincore.interfaces.IDCTimes(x).created,
        zope.dublincore.interfaces.IDCTimes(y).created))
    del workingcopy[ghosts[0].__name__]
