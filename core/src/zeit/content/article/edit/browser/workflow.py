# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.repository.interfaces import IAutomaticallyRenameable
from zeit.cms.workflow.interfaces import IPublishInfo
from zope.cachedescriptors.property import Lazy as cachedproperty
import json
import mock
import zeit.content.article.interfaces
import zeit.edit.browser.form
import zeit.workflow.interfaces
import zope.component
import zope.formlib.form
import zope.formlib.interfaces
import zope.formlib.widget
import zope.i18n


class WorkflowTimeContainer(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Workflow time')


class Timebased(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'timebased'
    undo_description = _('edit workflow time')
    form_fields = zope.formlib.form.FormFields(
        zeit.workflow.interfaces.IContentWorkflow).select('release_period')


class WorkflowContainer(zeit.edit.browser.form.FoldableFormGroup):
    """Article workflow forms."""

    title = _('Workflow')
    folded_workingcopy = False
    folded_repository = False


class Publish(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'publish'
    undo_description = _('edit workflow status')

    @property
    def form_fields(self):
        fields = zope.formlib.form.FormFields(
            zeit.workflow.interfaces.IContentWorkflow,
            zeit.content.article.interfaces.ICDSWorkflow).select(
            'edited', 'corrected', 'urgent', 'export_cds')
        if not self.can_checkout:
            fields += zope.formlib.form.FormFields(
                zeit.cms.content.interfaces.ISemanticChange).select(
                'has_semantic_change')

        for name in ['edited', 'corrected']:
            fields[name].custom_widget = zeit.cms.browser.widget.CheckboxWidget
        return fields

    def setUpWidgets(self, *args, **kw):
        super(Publish, self).setUpWidgets(*args, **kw)
        if IPublishInfo(self.context).urgent:
            # XXX This needs a better mechanism.
            for name in ('corrected', 'edited'):
                self.widgets[name].extra = 'disabled="disabled"'
                self.widgets[name].vivi_css_class = 'disabled'
        self.widgets['export_cds'].vivi_css_class = 'visual-clear'

        items = list(self.widgets.__Widgets_widgets_items__)
        items.append(self._make_view_widget('edit.form.checkin-buttons'))
        if not self.can_checkout:
            items.insert(
                -1, self._make_view_widget('edit.form.checkin-errors'))
            items.insert(-1, self._make_view_widget('edit.form.timestamp'))
        self.widgets = zope.formlib.form.Widgets(items, prefix=self.prefix)

    def _make_view_widget(self, name):
        widget = ViewWidget(self.context, self.request, name)
        widget.setPrefix(self.prefix)
        return (None, widget)

    @cachedproperty
    def can_checkout(self):
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(self.context)
        return manager.canCheckout


class CheckinErrors(object):

    @cachedproperty
    def checkin_errors(self):
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(self.context)
        manager.canCheckin  # cause last_validation_error to be populated
        errors = manager.last_validation_error
        if (not errors
            # XXX stopgap so it doesn't break, see #10851
            or not isinstance(errors, list)):
            return []

        result = []
        for field, error in errors:
            # adapted from zope.formlib.form.FormBase.error_views
            view = zope.component.getMultiAdapter(
                (error, self.request),
                zope.formlib.interfaces.IWidgetInputErrorView)
            title = field.title
            if isinstance(title, zope.i18n.Message):
                title = zope.i18n.translate(title, context=self.request)
            result.append(dict(name=title, snippet=view.snippet()))
        return result


class WorkflowButtons(object):

    @cachedproperty
    def can_checkout(self):
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(self.context)
        return manager.canCheckout

    @cachedproperty
    def can_checkin(self):
        manager = zeit.cms.checkout.interfaces.ICheckinManager(self.context)
        return manager.canCheckin

    @cachedproperty
    def published(self):
        publish_info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        return publish_info.published

    @property
    def is_new(self):
        return IAutomaticallyRenameable(self.context).renameable

    @property
    def has_semantic_change(self):
        return zeit.cms.content.interfaces.ISemanticChange(
            self.context).has_semantic_change


class Timestamp(object):

    def show_semantic_change(self):
        sc = zeit.cms.content.interfaces.ISemanticChange(self.context)
        return ((not sc.has_semantic_change) and
                (sc.last_semantic_change is not None))

    def last_semantic_change(self):
        sc = zeit.cms.content.interfaces.ISemanticChange(self.context)
        if not sc.last_semantic_change:
            return ''
        return sc.last_semantic_change.strftime('%d.%m.%Y %H:%Mh')


class ViewWidget(zope.formlib.widget.BrowserWidget):

    field_css_class = ''

    def __init__(self, context, request, view):
        field = mock.Mock()
        field.__name__ = 'htmlcontent.%s' % id(self)
        super(ViewWidget, self).__init__(field, request)
        self.context = context
        self.request = request
        self.view = view
        self.label = None

    def __call__(self):
        view = zope.component.getMultiAdapter(
            (self.context, self.request), name=self.view)
        return view()
