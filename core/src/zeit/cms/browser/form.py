# Copyright (c) 2006-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
from zope.i18nmessageid import ZopeMessageFactory as _zope
import datetime
import gocept.form.grouped
import pytz
import zeit.cms.browser.view
import zeit.cms.checkout.interfaces
import zope.app.container.interfaces
import zope.app.pagetemplate
import zope.event
import zope.formlib.form
import zope.formlib.interfaces
import zope.interface.common.idatetime
import zope.interface.interfaces
import zope.schema
import zope.security.proxy


REMAINING_FIELDS = object()


def apply_changes_with_setattr(context, form_fields, data, adapters=None):
    if adapters is None:
        adapters = {}

    changed = False

    for form_field in form_fields:
        field = form_field.field

        name = form_field.__name__
        newvalue = data.get(name, form_field)  # using form_field as marker
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
            try:
                setattr(adapter, name, newvalue)
            except AttributeError:
                pass

    return changed


MARKER = object()


def apply_default_values(context, interface):
    """Apply default values from ``interface`` to ``context``."""
    for name, field in zope.schema.getFields(interface).items():
        if field.readonly:
            continue
        __traceback_info__ = (name,)
        default = getattr(field, 'default')
        # don't set None values (#9406)
        if default is None:
            continue
        current = getattr(context, name, MARKER)
        # don't cause a field to be written unnecessarily
        if current == default:
            continue
        # if a value exists, don't overwrite it if it's valid (#10362)
        if current is not MARKER and current is not field.missing_value:
            field = field.bind(context)
            try:
                field.validate(current)
            except zope.schema.ValidationError:
                pass
            else:
                continue
        # now we have both an attribute without a meaningful value and a
        # meaningful value to set it to
        setattr(context, name, default)


class WidgetCSSMixin(object):
    """Form mix-in to manage CSS classes on widgets.

    - Adds "error" and "required" classes automatically.

    - Allows specifying a number of additional classes manually. This is done
      by setting the ``vivi_css_class`` attribute on each widget:

        def setUpWidgets(self, *args, **kw):
            super(ExampleForm, self).setUpWidgets(*args, **kw)
            self.widgets['foo'].vivi_css_class = 'barbaz qux'

    """

    def setUpWidgets(self, *args, **kw):
        super(WidgetCSSMixin, self).setUpWidgets(*args, **kw)
        for widget in self.widgets:
            widget.field_css_class = self._assemble_css_classes.__get__(widget)

    @staticmethod
    def _assemble_css_classes(widget):
        css_class = ['field', 'fieldname-' + widget.context.__name__]
        if widget.error():
            css_class.append('error')
        if widget.required:
            css_class.append('required')
        if zope.formlib.interfaces.ISimpleInputWidget.providedBy(widget):
            fieldtype = 'fieldtype-' + widget.type
            css_class.append(fieldtype)
        else:
            css_class.append('fieldtype-label')
        custom_css_class = getattr(widget, 'vivi_css_class', '')
        css_class.extend(custom_css_class.split())
        return ' '.join(css_class)


class PlaceholderMixin(object):

    def _is_textwidget(self, widget):
        if not zope.formlib.interfaces.ISimpleInputWidget.providedBy(widget):
            return False
        if widget.tag == 'textarea':
            return True
        if widget.tag == 'input':
            return widget.type == 'text' or not widget.type
        return False

    def setUpWidgets(self, *args, **kw):
        super(PlaceholderMixin, self).setUpWidgets(*args, **kw)
        for widget in self.widgets:
            if not self._is_textwidget(widget):
                continue
            placeholder = ''
            field = widget.context
            if zope.interface.interfaces.IElement.providedBy(field):
                placeholder = field.queryTaggedValue('placeholder')
            if not placeholder:
                placeholder = widget.label or ''
            placeholder = zope.i18n.translate(
                placeholder, context=self.request)
            widget.extra = ((widget.extra + ' ' if widget.extra else '') +
                            'placeholder="%s"' % placeholder)


class FormBase(zeit.cms.browser.view.Base, WidgetCSSMixin, PlaceholderMixin):

    widget_groups = ()
    template = zope.app.pagetemplate.ViewPageTemplateFile('grouped-form.pt')

    def applyChanges(self, object, data):
        return zope.formlib.form.applyChanges(
            object, self.form_fields, data, self.adapters)

    def render(self):
        self._send_message()
        if self.status and not self.errors:
            # rendered w/o error
            next_url = self.nextURL()
            if next_url is not None:
                return self.redirect(next_url)
        return super(FormBase, self).render()

    def _send_message(self):
        """Send message from self.status and self.errors via flashmessage."""
        if self.errors:
            for error in self.errors:
                message = error.doc()
                title = getattr(error, 'widget_title', None)  # duck typing
                translated = zope.i18n.translate(
                    message, context=self.request, default=message)
                if title:
                    if isinstance(title, zope.i18n.Message):
                        title = zope.i18n.translate(
                            title, context=self.request)
                    message = '%s: %s' % (title, translated)
                else:
                    message = translated
                self.send_message(message, type='error')
        elif self.status:
            self.send_message(self.status)


class AddFormBase(object):
    """This class provides mechanics for adding that are independent of
    rendering the form as a whole page or subpage/lightbox form.
    """

    factory = None
    next_view = None
    cancel_next_view = None
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

    def add(self, object, container=None):
        if container is None:
            container = self.context
        chooser = zope.app.container.interfaces.INameChooser(container)
        name = chooser.chooseName(self.suggestName(object), object)
        container[name] = object
        object = container[name]

        # Check the document out right away (if possible).
        if self.checkout:
            manager = zeit.cms.checkout.interfaces.ICheckoutManager(
                container[name], None)
            if manager is not None and manager.canCheckout:
                object = manager.checkout()
                self._checked_out = True

        self._created_object = object
        self._finished_add = True

    def cancelNextURL(self):
        return self.url('@@' + self.cancel_next_view)

    @zope.formlib.form.action(
        _("Cancel"),
        validator=lambda *a: (),
        condition=lambda form, action: form.cancel_next_view is not None)
    def cancel(self, action, data):
        url = self.cancelNextURL()
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
        return self.url(self._created_object, '@@' + view)


class AddForm(AddFormBase, FormBase, gocept.form.grouped.AddForm):
    """Add form."""


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
            view = '@@' + self.redirect_to_view

        return self.url(new_context, view)

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
