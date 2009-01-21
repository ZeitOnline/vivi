# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.checkout.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workingcopy.interfaces
import zeit.cms.workingcopy.workingcopy
import zope.app.container.interfaces
import zope.app.locking.interfaces
import zope.cachedescriptors.property
import zope.component
import zope.event
import zope.interface


class CheckoutManager(object):

    zope.interface.implements(
        zeit.cms.checkout.interfaces.ICheckoutManager,
        zeit.cms.checkout.interfaces.ICheckinManager)
    zope.component.adapts(zeit.cms.interfaces.ICMSContent)

    def __init__(self, context):
        self.context = context
        self.__parent__ = context

    @property
    def canCheckout(self):
        if not zeit.cms.repository.interfaces.IRepositoryContent.providedBy(
            self.context):
            return False
        lockable = zope.app.locking.interfaces.ILockable(self.context)
        if lockable.locked() and not lockable.ownLock():
            return False
        if zeit.cms.workingcopy.interfaces.ILocalContent(
            self.context, None) is None:
            return False
        for obj in self.workingcopy.values():
            if (zeit.cms.interfaces.ICMSContent.providedBy(obj)
                and obj.uniqueId == self.context.uniqueId):
                return False
        return True

    def checkout(self, event=True, temporary=False):
        if not self.canCheckout:
            raise zeit.cms.checkout.interfaces.CheckinCheckoutError(
                "Cannot checkout.")
        lockable = zope.app.locking.interfaces.ILockable(self.context)
        if not lockable.locked():
            try:
                lockable.lock(timeout=3600)
            except zeit.connector.interfaces.LockingError, e:
                # This is to catch a race condition when the object is locked
                # by another process/thread between the lock check above and
                # here.
                raise zeit.cms.checkout.interfaces.CheckinCheckoutError(
                    *e.args)

        if temporary:
            workingcopy = zeit.cms.workingcopy.workingcopy.Workingcopy()
        else:
            workingcopy = self.workingcopy

        if event:
            zope.event.notify(
                zeit.cms.checkout.interfaces.BeforeCheckoutEvent(
                    self.context, workingcopy, self.principal))
        content = zeit.cms.workingcopy.interfaces.ILocalContent(self.context)
        namechooser = zope.app.container.interfaces.INameChooser(workingcopy)
        name = namechooser.chooseName(content.__name__, content)
        added = workingcopy[name] = content

        if event:
            zope.event.notify(
                zeit.cms.checkout.interfaces.AfterCheckoutEvent(
                    added, workingcopy, self.principal))

        return workingcopy[name]

    @property
    def canCheckin(self):
        if not zeit.cms.workingcopy.interfaces.ILocalContent.providedBy(
            self.context):
            return False
        lockable = zope.app.locking.interfaces.ILockable(self.context)
        if not lockable.ownLock() and lockable.locked():
            return False
        return True

    def checkin(self, event=True):
        if not self.canCheckin:
            raise zeit.cms.checkout.interfaces.CheckinCheckoutError(
                "Cannot checkin.")
        workingcopy =  self.context.__parent__
        if event:
            zope.event.notify(
                zeit.cms.checkout.interfaces.BeforeCheckinEvent(
                    self.context, workingcopy, self.principal))
        unique_id = self.context.uniqueId
        added = zeit.cms.repository.interfaces.IRepositoryContent(self.context)
        del workingcopy[self.context.__name__]
        if event:
            zope.event.notify(
                zeit.cms.checkout.interfaces.AfterCheckinEvent(
                    added, workingcopy, self.principal))
        try:
            lockable = zope.app.locking.interfaces.ILockable(added)
            lockable.unlock()
        except zope.app.locking.interfaces.LockingError:
            # object was not locked
            pass
        return added

    @zope.cachedescriptors.property.Lazy
    def workingcopy(self):
        return zeit.cms.workingcopy.interfaces.IWorkingcopy(self.principal)

    @zope.cachedescriptors.property.Lazy
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    @zope.cachedescriptors.property.Lazy
    def principal(self):
        # Find the current principal. Note that it is possible for there
        # to be more than one principal - in this case we throw an error.
        interaction = zope.security.management.getInteraction()
        principal = None
        for p in interaction.participations:
            if principal is None:
                principal = p.principal
            else:
                raise ValueError("Multiple principals found")
        if principal is None:
            raise ValueError("No principal found")
        return principal


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zope.app.container.interfaces.IObjectRemovedEvent)
def unlockOnWorkingcopyDelete(context, event):
    """When the user deletes content from the working copy we see if this user
    has it locked. If so unlock it.

    """
    if not zeit.cms.workingcopy.interfaces.IWorkingcopy.providedBy(
        event.oldParent):
        return
    lockable = zope.app.locking.interfaces.ILockable(context)
    if lockable.ownLock():
        lockable.unlock()
