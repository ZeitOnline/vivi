# Copyright (c) 2006-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime
import os.path

import pytz

import zope.event
import zope.formlib.form
import zope.interface.common.idatetime

import zope.app.container.interfaces
import zope.app.pagetemplate
from zope.i18nmessageid import ZopeMessageFactory as _zope

import gocept.form.grouped

import zeit.cms.browser.view
import zeit.cms.checkout.interfaces
from zeit.cms.i18n import MessageFactory as _


REMAINING_FIELDS = object()


def apply_changes_with_setattr(context, form_fields, data, adapters=None):
    if adapters is None:
        adapters = {}

    changed = False

    for form_field in form_fields:
        field = form_field.field

        name = form_field.__name__
        newvalue = data.get(name, form_field) # using form_field as marker
        if newvalue is form_field:
            continue

        # Adapt context, if necessary
        interface = form_field.interface
        adapter = adapters.get(interface)
        if adapter is None:
            if interface is None:
                adapter = context
            else:
                adapter = interface(context)
            adapters[interface] = adapter

        if field.get(adapter) != newvalue:
            changed = True
            setattr(adapter, name, newvalue)

    return changed


class FormBase(zeit.cms.browser.view.Base):

    widget_groups = ()
    template = zope.app.pagetemplate.ViewPageTemplateFile(
        os.path.join(os.path.dirname(__file__), 'grouped-form.pt'))

    def applyChanges(self, object, data):
        return zope.formlib.form.applyChanges(
            object, self.form_fields, data, self.adapters)

    def render(self):
        self._send_message()
        if self.status and not self.errors:
            # rendered w/o error
            next_url = self.nextURL()
            if next_url is not None:
                #self.send_message(self.status)  # XXX
                return self.request.response.redirect(next_url)
        return super(FormBase, self).render()

    def _send_message(self):
        """Send message from self.status and self.errors via flashmessage."""
        if self.errors:
            for error in self.errors:
                message = error.doc()
                title = getattr(error, 'widget_title', None) # duck typing
                translated = zope.i18n.translate(
                    message, context=self.request, default=message)
                if title:
                    if isinstance(title, zope.i18n.Message):
                        title = zope.i18n.translate(title, context=self.request)
                    message = '%s: %s' % (title, translated)
                else:
                    message = translated
                self.send_message(message, type='error')
        elif self.status:
            self.send_message(self.status)


class AddForm(FormBase, gocept.form.grouped.AddForm):
    """Add form."""

    factory = None
    next_view = None
    checkout = True

    _checked_out = False

    def applyChanges(self, object, data):
        return apply_changes_with_setattr(
            object, self.form_fields, data, self.adapters)

    def create(self, data):
        if self.factory is None:
            raise ValueError("No factory specified.")
        new_object = self.factory()
        self.applyChanges(new_object, data)
        return new_object

    @zope.formlib.form.action(_("Add"),
                              condition=zope.formlib.form.haveInputWidgets)
    def handle_add(self, action, data):
        self.createAndAdd(data)

    def add(self, object):
        chooser = zope.app.container.interfaces.INameChooser(self.context)
        name = chooser.chooseName(self.suggestName(object), object)
        self.context[name] = object
        object = self.context[name]

        # Check the document out right away (if possible).
        if self.checkout:
            manager = zeit.cms.checkout.interfaces.ICheckoutManager(
                self.context[name], None)
            if manager is not None and manager.canCheckout:
                object = manager.checkout()
                self._checked_out = True

        self._created_object = object
        self._finished_add = True

    @zope.formlib.form.action(_("Cancel"), validator=lambda *a: ())
    def cancel(self, action, data):
        url = zope.component.getMultiAdapter(
            (self.context, self.request),
            name="absolute_url")()
        self.request.response.redirect(url)

    def suggestName(self, object):
        return object.__name__

    def nextURL(self):
        if self.next_view:
            view = self.next_view
        elif self._checked_out:
            view = 'edit.html'
        else:
            view = 'view.html'
        url = zope.component.getMultiAdapter(
            (self._created_object, self.request), name='absolute_url')()
        return '%s/@@%s' % (url, view)


class EditForm(FormBase, gocept.form.grouped.EditForm):
    """Edit form."""

    title = _("Edit")
    redirect_to_parent_after_edit = False
    redirect_to_view = None

    def nextURL(self):
        if (not self.redirect_to_parent_after_edit
            and not self.redirect_to_view):
            return None

        new_context = self.context
        if self.redirect_to_parent_after_edit:
            new_context = new_context.__parent__

        view = ''
        if self.redirect_to_view:
            view = '/@@%s' % self.redirect_to_view

        return '%s%s' % (
            zope.component.getMultiAdapter(
                (new_context, self.request), name='absolute_url')(),
            view)

    def applyChanges(self, data):
        """Apply changes and set message."""
        if zope.formlib.form.applyChanges(
            self.context, self.form_fields, data, self.adapters):
            zope.event.notify(
                zope.lifecycleevent.ObjectModifiedEvent(self.context))
            formatter = self.request.locale.dates.getFormatter(
                'dateTime', 'medium')

            try:
                time_zone = zope.interface.common.idatetime.ITZInfo(
                    self.request)
            except TypeError:
                time_zone = pytz.UTC

            self.status = _zope(
                "Updated on ${date_time}",
                mapping={'date_time': formatter.format(
                    datetime.datetime.now(time_zone))})
        else:
            self.status = _('No changes')

    @zope.formlib.form.action(
        _('Apply'), condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        self.applyChanges(data)


class DisplayForm(FormBase, gocept.form.grouped.DisplayForm):
    """Display form."""

    title = _("View")
