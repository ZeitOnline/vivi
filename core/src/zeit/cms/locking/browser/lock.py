# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.form.grouped
import zeit.cms.locking.browser.interfaces
import zeit.cms.locking.interfaces
import zeit.connector.interfaces
import zope.cachedescriptors.property
import zope.formlib.form
import zope.i18n
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

    @zope.formlib.form.action(_('Steal lock'),
                              condition=_stealable)
    def steal(self, action, data):
        old_locker = self.lockable.locker()
        self.lockable.breaklock()
        self.lockable.lock()
        self.send_message(
            _('The lock on "${name}" has been stolen from "${old_locker}".',
              mapping=dict(
                  name=self.context.__name__,
                  old_locker=old_locker)))

    @zope.formlib.form.action(_('Lock'),
                             condition=_lockable)
    def lock(self, action, data):
        self.lockable.lock()
        self.send_message(
            _('"${name}" has been locked.',
              mapping=dict(name=self.context.__name__)))

    @zope.formlib.form.action(_('Unlock'),
                             condition=_unlockable)
    def unlock(self, action, data):
        self.lockable.unlock()
        self.send_message(
            _('"${name}" has been unlocked.',
              mapping=dict(name=self.context.__name__)))

    @zope.cachedescriptors.property.Lazy
    def lockable(self):
        return zope.app.locking.interfaces.ILockable(self.context)

    def setUpWidgets(self, ignore_request=False):
        self.widgets = zope.formlib.form.setUpDataWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            data=self.get_data(), for_display=True,
            ignore_request=ignore_request)


class MenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):

    title = _('Manage lock')

    def img_tag(self):
        return zope.component.queryMultiAdapter(
            (self.context, self.request),
            name='get_locking_indicator')

    @zope.cachedescriptors.property.Lazy
    def lockable(self):
        return zope.app.locking.interfaces.ILockable(self.context, None)

    def update(self):
        super(MenuItem, self).update()

    def render(self):
        if self.lockable is None:
            return ''
        return super(MenuItem, self).render()


def get_locking_indicator(context, request):
    lockable = zope.app.locking.interfaces.ILockable(context, None)
    if lockable is None:
        return ''
    locked = lockable.locked()
    mylock = locked and lockable.ownLock()
    if mylock:
        img = 'lock-closed-mylock'
        title = _('Locked by you')
    elif locked:
        img = 'lock-closed'
        authentication = zope.component.getUtility(
            zope.app.security.interfaces.IAuthentication)
        locker = lockable.locker()
        try:
            locker = authentication.getPrincipal(locker).title
        except zope.app.security.interfaces.PrincipalLookupError:
            pass
        title = _('Locked by ${user}',
                  mapping=dict(user=lockable.locker()))
    else:
        img = 'lock-open'
        title = _('Not locked')
    resource_url = zope.component.getMultiAdapter(
        (request,), name='zeit.cms')()
    title = zope.i18n.translate(title, context=request)
    return '<img src="%s/icons/%s.png" title="%s" class="%s" />' % (
        resource_url, img, title, img)


def get_locking_indicator_for_listing(context, request):
    return zope.component.getMultiAdapter(
        (context.context, request), name='get_locking_indicator')
