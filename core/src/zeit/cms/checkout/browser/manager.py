from zeit.cms.i18n import MessageFactory as _
import transaction
import urllib.parse
import zeit.cms.browser.menu
import zeit.cms.browser.view
import zeit.cms.checkout.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
import zope.browser.interfaces
import zope.cachedescriptors.property
import zope.component
import zope.dublincore.interfaces
import zope.formlib.form
import zope.i18n


class Checkout(zeit.cms.browser.view.Base):

    def __call__(self):
        checked_out = None
        try:
            checked_out = self.manager.checkout()
            self.send_message(_('"${name}" has been checked out.',
                                mapping=dict(name=self.context.__name__)))
        except zeit.cms.checkout.interfaces.CheckinCheckoutError:
            # if the failure is because the object is already checked out,
            # we'll just use that one instead of complaining
            for obj in self.manager.workingcopy.values():
                if (zeit.cms.interfaces.ICMSContent.providedBy(obj) and
                        obj.uniqueId == self.context.uniqueId):
                    checked_out = obj
                    break
            # checkout failed for a different reason
            if checked_out is None:
                raise
            self.send_message(_('"${name}" was already checked out.',
                                mapping=dict(name=self.context.__name__)))

        new_view = None
        came_from = self.request.form.get('came_from')
        if came_from is not None:
            new_view = zope.component.queryAdapter(
                self.context,
                zeit.cms.browser.interfaces.IEditViewName,
                name=came_from)
        if new_view is None:
            new_view = 'edit.html'
        new_url = self.url(checked_out, '@@' + new_view)
        # XXX type conversion would be so nice
        if self.request.form.get('redirect', '').lower() == 'false':
            # XXX redirect=False now has two meanings:
            # 1. don't redirect, 2. don't use any view
            return self.url(checked_out)
        else:
            self.request.response.redirect(new_url)

    @property
    def canCheckout(self):
        return self.manager.canCheckout

    @zope.cachedescriptors.property.Lazy
    def manager(self):
        return zeit.cms.checkout.interfaces.ICheckoutManager(self.context)


class CheckinAndRedirect:

    def perform_checkin(self, semantic_change=None, event=True,
                        ignore_conflicts=False):
        try:
            checked_in = self.manager.checkin(
                semantic_change=semantic_change, event=event,
                ignore_conflicts=ignore_conflicts)
        except zeit.cms.repository.interfaces.ConflictError:
            return self._handle_conflict()
        else:
            if ignore_conflicts:
                self.send_message(
                    _('"${name}" has been checked in. Conflicts were ignored.',
                      mapping=dict(name=checked_in.__name__)))
            else:
                self.send_message(_('"${name}" has been checked in.',
                                    mapping=dict(name=checked_in.__name__)))
            return self._handle_checked_in(checked_in)

    def _handle_checked_in(self, checked_in):
        new_view = None
        came_from = self.request.form.get('came_from')
        if came_from is not None:
            new_view = zope.component.queryAdapter(
                self.context,
                zeit.cms.browser.interfaces.IDisplayViewName,
                name=came_from)
        if new_view is None:
            new_view = 'view.html'
        new_url = self.url(checked_in, '@@' + new_view)
        if self.request.form.get('redirect', '').lower() == 'false':
            return self.url(checked_in)
        else:
            return self.request.response.redirect(new_url)

    def _handle_conflict(self):
        transaction.doom()
        if self.request.form.get('redirect', '').lower() == 'false':
            raise zeit.cms.repository.interfaces.ConflictError(
                self.context.uniqueId,
                _('There was a conflict while adding ${name}',
                  mapping=dict(name=self.context.uniqueId)))
        view = zope.component.getMultiAdapter(
            (self.context, self.request),
            zope.browser.interfaces.IBrowserView,
            name='checkin-conflict-error')
        return view()

    @property
    def canCheckin(self):
        return self.manager.canCheckin

    @zope.cachedescriptors.property.Lazy
    def manager(self):
        return zeit.cms.checkout.interfaces.ICheckinManager(self.context)


class Checkin(zeit.cms.browser.view.Base, CheckinAndRedirect):

    def __call__(self, semantic_change=True, event=True,
                 ignore_conflicts=False):
        if semantic_change == 'None':
            semantic_change = None
        else:
            semantic_change = bool(semantic_change)
        return self.perform_checkin(
            semantic_change, bool(event), bool(ignore_conflicts))


class CheckinConflictError(zeit.cms.browser.view.Base):

    @zope.cachedescriptors.property.Lazy
    def obj_in_repository(self):
        return zeit.cms.interfaces.ICMSContent(self.context.uniqueId, None)

    @property
    def remote_information(self):
        if self.obj_in_repository is None:
            return zope.i18n.translate(
                _('The object was removed from the repository.'),
                context=self.request)
        view = zope.component.getMultiAdapter(
            (self.obj_in_repository, self.request),
            name='checkin-conflict-error-information')
        return view()

    @property
    def local_information(self):
        view = zope.component.getMultiAdapter(
            (self.context, self.request),
            name='checkin-conflict-error-information')
        return view()

    def render(self):
        if ('checkin' in self.request.form or
                'checkin-correction' in self.request.form):
            self.checkin()
        elif 'delete' in self.request.form:
            self.delete()
        elif 'cancel' in self.request.form:
            self.cancel()
        else:
            return super().render()

    def checkin(self):
        if 'checkin' in self.request.form:
            semantic_change = 'true'
        else:
            semantic_change = self.request.get('semantic_change', '')
        self.redirect(self.url(
            self.context, '@@checkin?%s' % urllib.parse.urlencode(dict(
                came_from=self.request.get('came_from', ''),
                ignore_conflicts='true',
                semantic_change=semantic_change,
            ))))

    def delete(self):
        target = self.obj_in_repository
        if target is None:
            target = self.context.__parent__
        del self.context.__parent__[self.context.__name__]
        self.redirect(self.url(target))

    def cancel(self):
        self.redirect(self.url(
            self.context, '@@' + self.request.get('came_from', '')))


class CheckinConflictErrorInformation(zope.formlib.form.SubPageDisplayForm):

    form_field_base = zope.formlib.form.FormFields(
        zeit.cms.workflow.interfaces.IModified)

    form_fields = form_field_base.select('last_modified_by')

    def __init__(self, context, request):
        super().__init__(context, request)
        if zeit.cms.workflow.interfaces.IModified(
                self.context).date_last_checkout:
            self.form_fields += self.form_field_base.select(
                'date_last_checkout')
        else:
            # Backwards-compatibility for articles that have not been checked
            # out since date_last_checkout was introduced.
            self.form_fields += self.form_field_base.select(
                'date_last_modified')


class MenuItem(zeit.cms.browser.menu.ActionMenuItem):

    weight = -10

    @property
    def action(self):
        view_name = self.__parent__.__name__
        return '@@%s?came_from=%s' % (self.base_action, view_name)

    def render(self):
        if self.is_visible():
            return super().render()
        return ''


class CheckoutMenuItem(MenuItem):
    """MenuItem for checking out."""

    title = _('Checkout ^O')
    base_action = 'checkout'
    accesskey = 'o'

    def is_visible(self):
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(self.context)
        return manager.canCheckout


class CheckinMenuItem(MenuItem):
    """MenuItem for checking in."""

    title = _('Checkin ^I')
    base_action = 'checkin'
    accesskey = 'i'
    rel = 'zeit.cms.follow_with_lock'

    def is_visible(self):
        manager = zeit.cms.checkout.interfaces.ICheckinManager(self.context)
        return manager.canCheckin

    @property
    def action(self):
        action = super().action
        return action + '&semantic_change=None'
