# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.cms.checkout.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workingcopy.interfaces
import zeit.cms.workingcopy.workingcopy
import zeit.objectlog.interfaces
import zope.app.container.interfaces
import zope.app.locking.interfaces
import zope.cachedescriptors.property
import zope.component
import zope.dublincore.interfaces
import zope.event
import zope.interface
import zope.security.proxy


class CheckoutManager(object):

    zope.interface.implements(
        zeit.cms.checkout.interfaces.ICheckoutManager,
        zeit.cms.checkout.interfaces.ICheckinManager)
    zope.component.adapts(zeit.cms.interfaces.ICMSContent)

    def __init__(self, context):
        self.context = context
        self.__parent__ = context
        self.last_validation_error = None

    @property
    def canCheckout(self):
        try:
            self._guard_checkout()
        except zeit.cms.checkout.interfaces.CheckinCheckoutError:
            return False
        return True

    def _guard_checkout(self):
        lockable = zope.app.locking.interfaces.ILockable(self.context, None)
        if (lockable is not None and
            lockable.locked() and not lockable.ownLock()):
            raise zeit.cms.checkout.interfaces.CheckinCheckoutError(
                self.context.uniqueId,
                _('The content object is locked by ${name}.', mapping=dict(
                    name=lockable.locker())))
        if zeit.cms.workingcopy.interfaces.ILocalContent(
            self.context, None) is None:
            raise zeit.cms.checkout.interfaces.CheckinCheckoutError(
                self.context.uniqueId,
                'Could not adapt content to ILocalContent')
        for obj in self.workingcopy.values():
            if (zeit.cms.interfaces.ICMSContent.providedBy(obj)
                and obj.uniqueId == self.context.uniqueId):
                raise zeit.cms.checkout.interfaces.CheckinCheckoutError(
                    self.context.uniqueId,
                    _('The content you tried to check out is already in your '
                      'working copy.'))
        return True

    def checkout(self, event=True, temporary=False):
        self._guard_checkout()
        lockable = zope.app.locking.interfaces.ILockable(self.context, None)
        if lockable is not None and not lockable.locked():
            timeout = 30 if temporary else 3600
            try:
                lockable.lock(timeout=timeout)
            except zope.app.locking.interfaces.LockingError, e:
                # This is to catch a race condition when the object is locked
                # by another process/thread between the lock check above and
                # here.
                raise zeit.cms.checkout.interfaces.CheckinCheckoutError(
                    *e.args)

        if temporary:
            workingcopy = zeit.cms.workingcopy.workingcopy.Workingcopy(
                temporary=True)
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
            self.last_validation_error = _('Object is not local content')
            return False
        lockable = zope.app.locking.interfaces.ILockable(self.context, None)
        if (lockable is not None
            and not lockable.ownLock() and lockable.locked()):
            self.last_validation_error = _('Cannot acquire lock')
            return False
        workingcopy = self.context.__parent__
        if not workingcopy.temporary:
            event = zeit.cms.checkout.interfaces.ValidateCheckinEvent(
                self.context, workingcopy, self.principal)
            zope.event.notify(event)
            self.last_validation_error = event.vetoed
            if self.last_validation_error is not None:
                return False
        return True

    def checkin(self, event=True, semantic_change=None,
                ignore_conflicts=False, publishing=False):
        if not self.canCheckin:
            reason = self.last_validation_error
            if reason is None:
                reason = _('Unknown error')
            raise zeit.cms.checkout.interfaces.CheckinCheckoutError(
                self.context.uniqueId, 'Cannot checkin: %s' % reason)
        workingcopy = self.context.__parent__
        sc = zeit.cms.content.interfaces.ISemanticChange(self.context)
        if semantic_change is None:
            semantic_change = sc.has_semantic_change
        if semantic_change:
            dc = zope.dublincore.interfaces.IDCTimes(self.context)
            sc = zope.security.proxy.removeSecurityProxy(sc)
            sc.last_semantic_change = dc.modified
        if event:
            zope.event.notify(
                zeit.cms.checkout.interfaces.BeforeCheckinEvent(
                    self.context, workingcopy, self.principal, publishing))
        if ignore_conflicts:
            adapter_name = u'non-conflicting'
        else:
            adapter_name = u''
        added = zope.component.getAdapter(
            self.context,
            zeit.cms.checkout.interfaces.IRepositoryContent,
            name=adapter_name)
        del workingcopy[self.context.__name__]
        if event:
            zope.event.notify(
                zeit.cms.checkout.interfaces.AfterCheckinEvent(
                    added, workingcopy, self.principal, publishing))
        lockable = zope.app.locking.interfaces.ILockable(added, None)
        if lockable is not None:
            try:
                lockable.unlock()
            except zope.app.locking.interfaces.LockingError:
                # object was not locked
                pass
        return added

    def delete(self):
        workingcopy = self.context.__parent__
        zope.event.notify(
            zeit.cms.checkout.interfaces.BeforeDeleteEvent(
                self.context, workingcopy, self.principal))
        del workingcopy[self.context.__name__]
        zope.event.notify(
            zeit.cms.checkout.interfaces.AfterDeleteEvent(
                self.context, workingcopy, self.principal))

    @zope.cachedescriptors.property.Lazy
    def workingcopy(self):
        return zeit.cms.checkout.interfaces.IWorkingcopy(None)

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


@grok.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zope.lifecycleevent.IObjectRemovedEvent)
def unlockOnWorkingcopyDelete(context, event):
    """When the user deletes content from the working copy we see if this user
    has it locked. If so unlock it.

    """
    if not zeit.cms.checkout.interfaces.IWorkingcopy.providedBy(
        event.oldParent):
        return
    # Get content from repository
    content = zeit.cms.interfaces.ICMSContent(context.uniqueId, None)
    lockable = zope.app.locking.interfaces.ILockable(content, None)
    if lockable is not None and lockable.ownLock():
        lockable.unlock()


@grok.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IAfterDeleteEvent)
def deleteNewContentFromRepositoryOnWorkingcopyDelete(context, event):
    """When the user deletes content from the working copy which has never
    been checked in, we delete the empty object from the repository as well.

    """
    renameable = zeit.cms.repository.interfaces.IAutomaticallyRenameable(
            context, None)
    if renameable is None or not renameable.renameable:
        return
    content = zeit.cms.interfaces.ICMSContent(context.uniqueId, None)
    if content is not None:
        del content.__parent__[content.__name__]


@grok.subscribe(zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def log_checkin(event):
    if event.publishing:
        return
    zeit.objectlog.interfaces.ILog(event.object).log(_('Checked in'))
