# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.cachedescriptors.property
import zope.formlib.form

import gocept.form.grouped

import zeit.connector.interfaces

import zeit.cms.locking.interfaces
import zeit.cms.locking.browser.interfaces
from zeit.cms.i18n import MessageFactory as _


def _stealable(form, action):
    return form.lockable.isLockedOut()

def _unlockable(form, action):
    return form.lockable.ownLock()

def _lockable(form, action):
    return not form.lockable.locked()


class Lock(zeit.cms.browser.lightbox.Form):

    title = _("Locks")

    form_fields = zope.formlib.form.Fields(
        zeit.cms.locking.browser.interfaces.ILockFormSchema)

    def get_data(self):
        lockable = self.lockable
        lockinfo = lockable.getLockInfo()
        locked_until = None
        created = None

        if zeit.cms.locking.interfaces.ILockInfo.providedBy(lockinfo):
            locked_until = lockinfo.locked_until

        return dict(
            locked=lockable.locked(),
            locker=lockable.locker(),
            locked_until=locked_until,
        )

    @zope.formlib.form.action(_('Steal Lock'),
                              condition=_stealable)
    def steal(self, action, data):
        self.lockable.breaklock()

    @zope.formlib.form.action(_('Lock'),
                             condition=_lockable)
    def lock(self, action, data):
        self.lockable.lock()

    @zope.formlib.form.action(_('Unlock'),
                             condition=_unlockable)
    def unlock(self, action, data):
        self.lockable.unlock()

    @zope.cachedescriptors.property.Lazy
    def lockable(self):
        return zope.app.locking.interfaces.ILockable(self.context)

    def setUpWidgets(self, ignore_request=False):
        self.widgets = zope.formlib.form.setUpDataWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            data=self.get_data(), for_display=True,
            ignore_request=ignore_request)


class MenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):

    locked_icon = 'lock-closed.png'
    not_locked_icon = 'lock-open.png'
    own_lock_icon = 'lock-closed-mylock.png'

    @property
    def icon(self):
        if self.lockable.ownLock():
            icon = self.own_lock_icon
        elif self.lockable.locked():
            icon = self.locked_icon
        else:
            icon = self.not_locked_icon
        return '/@@/zeit.cms/icons/%s' % icon

    @zope.cachedescriptors.property.Lazy
    def lockable(self):
        return zope.app.locking.interfaces.ILockable(self.context)
