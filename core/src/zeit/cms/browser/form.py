from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zeit.cms.browser.view
import zeit.cms.checkout.interfaces
import zope.container.interfaces
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


class AttrDict(dict):
    """Offers dict-like API and property access to check invariants.

    This helper object is used to perform validations in views to access dicts
    like an object with attributes, which is how invariants normally access the
    data object.

    """

    def __getattr__(self, name):
        """Access dict-content like properties.

        Will raise NoInputData when key is not found, since validations are
        skipped when a required field is not present.

        """
        try:
            return self[name]
        except KeyError:
            raise zope.formlib.form.NoInputData()


class WidgetCSSMixin:
    """Form mix-in to manage CSS classes on widgets.

    - Adds "error" and "required" classes automatically.

    - Allows specifying a number of additional classes manually. This is done
      by setting the ``vivi_css_class`` attribute on each widget:

        def setUpWidgets(self, *args, **kw):
            super().setUpWidgets(*args, **kw)
            self.widgets['foo'].vivi_css_class = 'barbaz qux'

    """

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
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


class PlaceholderMixin:
    def _is_textwidget(self, widget):
        if not zope.formlib.interfaces.ISimpleInputWidget.providedBy(widget):
            return False
        if widget.tag == 'textarea':
            return True
        if widget.tag == 'input':
            return widget.type == 'text' or not widget.type
        return False

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        for widget in self.widgets:
            if not self._is_textwidget(widget):
                continue
            placeholder = ''
            field = widget.context
            if zope.interface.interfaces.IElement.providedBy(field):
                placeholder = field.queryTaggedValue('placeholder')
            if not placeholder:
                placeholder = widget.label or ''
            placeholder = zope.i18n.translate(placeholder, context=self.request)
            widget.extra = (
                widget.extra + ' ' if widget.extra else ''
            ) + 'placeholder="%s"' % placeholder


class CharlimitMixin:
    def set_charlimit(self, field_name):
        widget = self.widgets[field_name]
        field = widget.context
        limit = field.queryTaggedValue('zeit.cms.charlimit', field.max_length)
        if hasattr(widget, 'extra'):
            # i.e. we're not in read-only mode
            widget.extra += ' cms:charlimit="%s"' % limit


class FormBase(zeit.cms.browser.view.Base, WidgetCSSMixin, PlaceholderMixin):
    widget_groups = ()
    template = zope.app.pagetemplate.ViewPageTemplateFile('grouped-form.pt')

    def render(self):
        self._send_message()
        if self.status and not self.errors:
            # rendered w/o error
            next_url = self.nextURL()
            if next_url is not None:
                return self.redirect(next_url)
        return super().render()

    def _send_message(self):
        """Send message from self.status and self.errors via flashmessage."""
        if self.errors:
            for error in self.errors:
                message = error.doc()
                title = getattr(error, 'widget_title', None)  # duck typing
                translated = zope.i18n.translate(message, context=self.request, default=message)
                if title:
                    if isinstance(title, zope.i18n.Message):
                        title = zope.i18n.translate(title, context=self.request)
                    message = '%s: %s' % (title, translated)
                else:
                    message = translated
                self.send_message(message, type='error')
        elif self.status:
            self.send_message(self.status)


class AddFormBase:
    """This class provides mechanics for adding that are independent of
    rendering the form as a whole page or subpage/lightbox form.
    """

    factory = None
    widgets_of_new_object = True

    next_view = None
    cancel_next_view = None
    checkout = True

    _checked_out = False

    def applyChanges(self, object, data):
        return apply_changes_with_setattr(object, self.form_fields, data, self.adapters)

    def make_object(self):
        if self.factory is None:
            raise ValueError('No factory specified.')
        return self.factory()

    def setUpWidgets(self, ignore_request=False):
        if self.widgets_of_new_object:
            self.new_object = self.make_object()
        else:
            self.new_object = self.context
        return super().setUpWidgets(ignore_request)

    def _get_widgets(self, form_fields, ignore_request):
        return zope.formlib.form.setUpInputWidgets(
            form_fields, self.prefix, self.new_object, self.request, ignore_request=ignore_request
        )

    def create(self, data):
        if not self.widgets_of_new_object:
            self.new_object = self.make_object()
        self.applyChanges(self.new_object, data)
        return self.new_object

    @zope.formlib.form.action(_('Add'), condition=zope.formlib.form.haveInputWidgets)
    def handle_add(self, action, data):
        self.createAndAdd(data)

    def add(self, object, container=None, name=None):
        if container is None:
            container = self.context
        if name is None:
            chooser = zope.container.interfaces.INameChooser(container)
            name = chooser.chooseName(self.suggestName(object), object)
        container[name] = object
        object = container[name]

        # Check the document out right away (if possible).
        if self.checkout:
            manager = zeit.cms.checkout.interfaces.ICheckoutManager(container[name], None)
            if manager is not None and manager.canCheckout:
                object = manager.checkout()
                self._checked_out = True

        self._created_object = object
        self._finished_add = True

    def cancelNextURL(self):
        return self.url('@@' + self.cancel_next_view)

    @zope.formlib.form.action(
        _('Cancel'),
        validator=lambda *a: (),
        condition=lambda form, action: form.cancel_next_view is not None,
    )
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

    title = _('Edit')
    redirect_to_parent_after_edit = False
    redirect_to_view = None

    def nextURL(self):
        if not self.redirect_to_parent_after_edit and not self.redirect_to_view:
            return None

        new_context = self.context
        if self.redirect_to_parent_after_edit:
            new_context = new_context.__parent__

        view = ''
        if self.redirect_to_view:
            view = '@@' + self.redirect_to_view

        return self.url(new_context, view)

    @zope.formlib.form.action(_('Apply'), condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        """Overwritten to use custom translation for Apply."""
        super().handle_edit_action.success(data)


class DisplayForm(FormBase, gocept.form.grouped.DisplayForm):
    """Display form."""

    title = _('View')
