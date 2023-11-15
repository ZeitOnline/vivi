import zeit.cms.checkout.interfaces
import zeit.cms.clipboard.entry
import zeit.cms.clipboard.interfaces
import zeit.cms.interfaces
import zeit.ghost.interfaces
import zope.component
import zope.container.interfaces
import zope.interface


def create_ghost(content, workingcopy=None):
    if workingcopy is None:
        workingcopy = zeit.cms.checkout.interfaces.IWorkingcopy(None)
    _remove_excessive_ghosts(workingcopy)
    entry = zeit.cms.clipboard.entry.Entry(content)
    zope.interface.directlyProvides(entry, zeit.ghost.interfaces.IGhost)
    chooser = zope.container.interfaces.INameChooser(workingcopy)
    name = chooser.chooseName(content.__name__, entry)
    workingcopy[name] = entry


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent, zeit.cms.checkout.interfaces.IAfterCheckinEvent
)
def add_ghost_after_checkin(context, event):
    """Add a ghost for the checked in object."""
    create_ghost(context, event.workingcopy)


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent, zeit.cms.checkout.interfaces.IAfterCheckoutEvent
)
def remove_ghost_after_checkout(context, event):
    """Remove ghost of checked out object, if any."""
    workingcopy = event.workingcopy
    unique_id = context.uniqueId

    for name in list(workingcopy):
        # Make a list before iterating because the loop is modifying the
        # workingcopy
        content = workingcopy[name]
        if not zeit.cms.clipboard.interfaces.IObjectReference.providedBy(content):
            continue
        referenced = content.references
        if referenced is None or unique_id == content.references.uniqueId:
            del workingcopy[name]


TARGET_WORKINGCOPY_SIZE = 7


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent, zeit.cms.checkout.interfaces.IAfterCheckoutEvent
)
def remove_excessive_ghosts(context, event):
    _remove_excessive_ghosts(event.workingcopy)


def _remove_excessive_ghosts(workingcopy):
    while len(workingcopy) > TARGET_WORKINGCOPY_SIZE:
        ghost_removed = remove_oldest_ghost(workingcopy)
        if not ghost_removed:
            # no ghosts left to remove
            break


def remove_oldest_ghost(workingcopy):
    """Remove the oldest ghost in the workingcopy, if any."""
    ghosts = [
        content
        for content in workingcopy.values()
        if zeit.cms.clipboard.interfaces.IObjectReference.providedBy(content)
    ]
    if not ghosts:
        return False
    del workingcopy[ghosts[-1].__name__]
    return True
