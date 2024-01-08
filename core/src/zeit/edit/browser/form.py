import json

import zope.browserpage
import zope.formlib.form
import zope.formlib.interfaces
import zope.formlib.itemswidgets
import zope.formlib.source
import zope.formlib.widget

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.cms.browser.view
import zeit.cms.checkout.interfaces
import zeit.edit.browser.view


class Forms:
    """View that collects all inline forms."""


FormGroup = zope.viewlet.viewlet.SimpleViewletClass('layout.forms.pt')


class FoldableFormGroup(zope.viewlet.viewlet.SimpleViewletClass('layout.foldable-forms.pt')):
    folded_workingcopy = True
    folded_repository = True

    @property
    def folded(self):
        if zeit.cms.checkout.interfaces.ILocalContent.providedBy(self.context):
            return self.folded_workingcopy
        else:
            return self.folded_repository


FormLoader = zope.viewlet.viewlet.SimpleViewletClass('layout.form-loader.pt')


class InlineForm(
    zeit.cms.browser.form.WidgetCSSMixin,
    zeit.cms.browser.form.PlaceholderMixin,
    zope.formlib.form.SubPageEditForm,
    zeit.cms.browser.view.Base,
):
    template = zope.browserpage.ViewPageTemplateFile('inlineform.pt')

    css_class = None

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._signals = []

    def reload(self, element=None):
        if element is None:
            element = self.context
        self.signal('reload', element.__name__, self.url(element, '@@contents'))

    def signal(self, name, *args):
        self._signals.append({'name': name, 'args': args})

    @property
    def signals(self):
        return json.dumps(self._signals)

    @zope.formlib.form.action(_('Apply'), failure='success_handler')
    def handle_edit_action(self, action, data):
        return self.success_handler(action, data)

    def success_handler(self, action, data, errors=None):
        self._success_handler()
        return super().handle_edit_action.success(data)

    def _success_handler(self):
        pass

    def validate(self, action, data):
        errors = super().validate(action, data)
        self.get_all_input_even_if_invalid(data)
        return errors

    def get_all_input_even_if_invalid(self, data):
        # Since zope.formlib does not offer an API to the input value of a
        # widget regardless of validation errors, this is quite a bit of
        # guesswork, and not 100% complete (e.g. SequenceWidgets are not
        # handled here).
        form_prefix = zope.formlib.form.expandPrefix(self.prefix)
        for input, widget in self.widgets.__iter_input_and_widget__():
            if input and zope.formlib.interfaces.IInputWidget.providedBy(widget):
                name = zope.formlib.form._widgetKey(widget, form_prefix)
                try:
                    try:
                        # combination widget has a helper for us.
                        data[name] = widget.loadValueFromRequest()
                    except AttributeError:
                        if not hasattr(widget, '_toFieldValue'):
                            # e.g. SequenceWidget
                            continue
                        data[name] = widget._toFieldValue(widget._getFormInput() or widget._missing)
                except zope.formlib.interfaces.ConversionError:
                    pass

    def is_basic_display_widget(self, widget):
        # XXX kludgy. We want to express "is this a base widget out of
        # zope.formlib?" (since those are the ones we want to style differently
        # in readonly-mode).
        # We can't use IDisplayWidget, since a) some formlib
        # widgets don't provide it while b) some widgets we don't want to
        # include (like ObjectSequenceDisplayWidget) do provide it.
        return type(widget) in [
            zope.formlib.widget.DisplayWidget,
            zope.formlib.widget.UnicodeDisplayWidget,
            zope.formlib.source.SourceDisplayWidget,
            zope.formlib.itemswidgets.ItemDisplayWidget,
        ]
