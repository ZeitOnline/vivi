# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import json
import zeit.cms.browser.form
import zeit.cms.browser.view
import zeit.cms.checkout.interfaces
import zeit.edit.browser.view
import zope.app.pagetemplate
import zope.formlib.form
import zope.formlib.itemswidgets
import zope.formlib.source
import zope.formlib.widget


class Forms(object):
    """View that collects all inline forms."""


FormGroup = zope.viewlet.viewlet.SimpleViewletClass('layout.forms.pt')


class FoldableFormGroup(zope.viewlet.viewlet.SimpleViewletClass(
        'layout.foldable-forms.pt')):

    folded_workingcopy = True
    folded_repository = True

    @property
    def folded(self):
        if zeit.cms.checkout.interfaces.ILocalContent.providedBy(self.context):
            return self.folded_workingcopy
        else:
            return self.folded_repository


FormLoader = zope.viewlet.viewlet.SimpleViewletClass('layout.form-loader.pt')


class InlineForm(zeit.cms.browser.form.WidgetCSSMixin,
                 zeit.cms.browser.form.PlaceholderMixin,
                 zope.formlib.form.SubPageEditForm,
                 zeit.edit.browser.view.UndoableMixin,
                 zeit.cms.browser.view.Base):

    template = zope.app.pagetemplate.ViewPageTemplateFile('inlineform.pt')

    css_class = None

    def __init__(self, *args, **kw):
        super(InlineForm, self).__init__(*args, **kw)
        self._signals = []

    def signal(self, name, *args):
        self._signals.append(dict(name=name, args=args))

    @property
    def signals(self):
        return json.dumps(self._signals)

    @zope.formlib.form.action(_('Apply'))
    def handle_edit_action(self, action, data):
        self.mark_transaction_undoable()
        return super(InlineForm, self).handle_edit_action.success(data)

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
