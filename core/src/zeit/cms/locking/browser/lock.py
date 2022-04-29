from zeit.cms.i18n import MessageFactory as _
import json
import logging
import zeit.cms.locking.browser.interfaces
import zeit.cms.locking.interfaces
import zeit.connector.interfaces
import zope.cachedescriptors.property
import zope.formlib.form
import zope.i18n


log = logging.getLogger(__name__)


def _stealable(form, action):
    return (form.lockable.isLockedOut() and
            form.request.interaction.checkPermission(
                'zeit.ManageLocks', form.context))


def _unlockable(form, action):
    return form.lockable.ownLock()


def _lockable(form, action):
    return not form.lockable.locked()


class Lock(zeit.cms.browser.lightbox.Form):

    title = _("Locks")

    form_fields = zope.formlib.form.Fields(
        zeit.cms.locking.browser.interfaces.ILockFormSchema)
    display_only = True

    def get_data(self):
        lockable = self.lockable
        lockinfo = lockable.getLockInfo()
        locked_until = None

        if zeit.cms.locking.interfaces.ILockInfo.providedBy(lockinfo):
            locked_until = lockinfo.locked_until

        return dict(
            locked=lockable.locked(),
            locker=lockable.locker(),
            locked_until=locked_until,
        )

    @zope.formlib.form.action(_('Steal lock'), condition=_stealable)
    def steal(self, action, data):
        old_locker = self.lockable.locker()
        self.lockable.breaklock()
        self.lockable.lock()
        self.send_message(
            _('The lock on "${name}" has been stolen from "${old_locker}".',
              mapping=dict(
                  name=self.context.__name__,
                  old_locker=old_locker)))

    @zope.formlib.form.action(_('Lock'), condition=_lockable)
    def lock(self, action, data):
        self.lockable.lock()
        self.send_message(
            _('"${name}" has been locked.',
              mapping=dict(name=self.context.__name__)))

    @zope.formlib.form.action(_('Unlock'), condition=_unlockable)
    def unlock(self, action, data):
        self.lockable.unlock()
        self.send_message(
            _('"${name}" has been unlocked.',
              mapping=dict(name=self.context.__name__)))

    @zope.cachedescriptors.property.Lazy
    def lockable(self):
        return zope.app.locking.interfaces.ILockable(self.context)


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
    title = zope.i18n.translate(title, context=request)
    return '<img src="%s" title="%s" class="%s" />' % (
        zeit.cms.browser.view.resource_url(
            request, 'zeit.cms', 'icons/%s.png' % img), title, img)


def get_locking_indicator_for_listing(context, request):
    return zope.component.getMultiAdapter(
        (context.context, request), name='get_locking_indicator')


class API:

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/json')

        if 'uuid' in self.request.form:
            uniqueId = zeit.cms.content.contentuuid.resolve_uuid(
                zeit.cms.content.interfaces.IUUID(self.request.form['uuid']))
        elif 'irid' in self.request.form:
            uniqueId = resolve_article_id(self.request.form['irid'])
        elif 'uniqueId' in self.request.form:  # mostly for convenience/tests
            uniqueId = self.request.form['uniqueId']
            content = zeit.cms.interfaces.ICMSContent(uniqueId, None)
            if content is None:
                uniqueId = None
        else:
            self.request.response.setStatus(400)
            return json.dumps(
                {'message': 'GET parameter uniqueId uuid or irid is required'})
        if not uniqueId:
            self.request.response.setStatus(404)
            return json.dumps({'message': 'Content not found'})

        storage = zope.component.getUtility(
            zope.app.locking.interfaces.ILockStorage)
        lock = storage.getLock(DummyContent(uniqueId))
        if lock is not None:
            self.request.response.setStatus(409)
            result = {
                'locked': True,
                'owner': lock.principal_id,
                'until': (lock.locked_until.isoformat()
                          if lock.locked_until else None),
            }
        else:
            result = {'locked': False, 'owner': None, 'until': None}

        return json.dumps(result)


@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
class DummyContent:
    """Helper so we don't have to resolve ICMSContent, since ILockStorage uses a
    ICMSContent-based API, even though it only uses the uniqueId (to pass it to
    IConnector).
    """

    def __init__(self, uniqueId):
        self.uniqueId = uniqueId


ARTICLEID = zeit.connector.search.SearchVar(
    'article_id', 'http://namespaces.zeit.de/CMS/interred')


def resolve_article_id(irid):
    connector = zope.component.getUtility(
        zeit.connector.interfaces.IConnector)
    result = list(connector.search([ARTICLEID], ARTICLEID == irid))
    if not result:
        return None
    if len(result) > 1:
        log.critical('There are %s objects for irid %s. Using first one.' % (
            len(result), irid))
    return result[0][0]
