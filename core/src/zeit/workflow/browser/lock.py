# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime

import zope.cachedescriptors.property
import zope.component
import zope.i18nmessageid
import zope.formlib.form

import gocept.form.grouped

import zeit.connector.interfaces

import zeit.workflow.browser.interfaces


_ = zope.i18nmessageid.MessageFactory('zeit.cms')


def _stealable(form, action):
    return form.lockable.isLockedOut()

def _unlockable(form, action):
    return form.lockable.ownLock()

def _lockable(form, action):
    return not form.lockable.locked()


class Lock(zeit.cms.browser.form.FormBase, gocept.form.grouped.Form):

    title = _("Locks")

    form_fields = zope.formlib.form.Fields(
        zeit.workflow.browser.interfaces.ILockFormSchema)

    def get_data(self):
        lockable = self.lockable
        lockinfo = lockable.getLockInfo()
        locked_until = None
        created = None

        if zeit.cms.content.interfaces.ILockInfo.providedBy(lockinfo):
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

    def _get_widgets(self, form_fields, ignore_request=False):
        return zope.formlib.form.setUpDataWidgets(
            form_fields, self.prefix, self.context, self.request,
            data=self.get_data(), for_display=True,
            ignore_request=ignore_request)
