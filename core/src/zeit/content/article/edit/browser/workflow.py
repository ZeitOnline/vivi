from unittest import mock

from zope.cachedescriptors.property import Lazy as cachedproperty
import pendulum
import zc.form.browser.combinationwidget
import zope.app.pagetemplate
import zope.component
import zope.formlib.form
import zope.formlib.interfaces
import zope.formlib.sequencewidget
import zope.formlib.widget
import zope.i18n

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.repository.interfaces import IAutomaticallyRenameable
import zeit.content.article.interfaces
import zeit.edit.browser.form
import zeit.workflow.interfaces
import zeit.workflow.scheduled.interfaces


class WorkflowTimeContainer(zeit.edit.browser.form.FoldableFormGroup):
    title = _('Workflow time')


class Timebased(zeit.edit.browser.form.InlineForm):
    legend = _('')
    prefix = 'timebased'
    form_fields = zope.formlib.form.FormFields(zeit.workflow.interfaces.IContentWorkflow).select(
        'release_period'
    )


class WorkflowContainer(zeit.edit.browser.form.FoldableFormGroup):
    """Article workflow forms."""

    title = _('Workflow')
    folded_workingcopy = False
    folded_repository = False


class Publish(zeit.edit.browser.form.InlineForm):
    legend = _('')
    prefix = 'publish'

    @property
    def form_fields(self):
        fields = zope.formlib.form.FormFields(zeit.workflow.interfaces.IContentWorkflow).select(
            'edited', 'corrected', 'seo_optimized', 'urgent'
        )
        if not self.can_checkout:
            fields += zope.formlib.form.FormFields(
                zeit.cms.content.interfaces.ISemanticChange
            ).select('has_semantic_change')

        for name in ['edited', 'corrected', 'seo_optimized']:
            fields[name].custom_widget = zeit.cms.browser.widget.CheckBoxWidget
        return fields

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        items = list(self.widgets.__Widgets_widgets_items__)
        items.append(self._make_view_widget('edit.form.checkin-buttons'))
        if not self.can_checkout:
            items.insert(-1, self._make_view_widget('edit.form.checkin-errors'))
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


class CheckinErrors:
    @cachedproperty
    def checkin_errors(self):
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(self.context)
        _ = manager.canCheckin  # cause last_validation_error to be populated
        errors = manager.last_validation_error
        if (
            not errors
            or
            # XXX stopgap so it doesn't break, see #10851
            not isinstance(errors, list)
        ):
            return []

        result = []
        for field, error in errors:
            # adapted from zope.formlib.form.FormBase.error_views
            view = zope.component.getMultiAdapter(
                (error, self.request), zope.formlib.interfaces.IWidgetInputErrorView
            )
            title = field.title
            if isinstance(title, zope.i18n.Message):
                title = zope.i18n.translate(title, context=self.request)
            result.append({'name': title, 'snippet': view.snippet()})
        return result


class WorkflowButtons:
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
        return zeit.cms.content.interfaces.ISemanticChange(self.context).has_semantic_change


class Timestamp:
    def show_semantic_change(self):
        sc = zeit.cms.content.interfaces.ISemanticChange(self.context)
        return (not sc.has_semantic_change) and (sc.last_semantic_change is not None)

    def last_semantic_change(self):
        sc = zeit.cms.content.interfaces.ISemanticChange(self.context)
        if not sc.last_semantic_change:
            return ''
        tz = zope.interface.common.idatetime.ITZInfo(self.request)
        return sc.last_semantic_change.astimezone(tz).strftime('%d.%m.%Y %H:%Mh')


class ViewWidget(zope.formlib.widget.BrowserWidget):
    field_css_class = ''

    def __init__(self, context, request, view):
        field = mock.Mock()
        field.__name__ = 'htmlcontent.%s' % id(self)
        super().__init__(field, request)
        self.context = context
        self.request = request
        self.view = view
        self.label = None

    def __call__(self):
        view = zope.component.getMultiAdapter((self.context, self.request), name=self.view)
        return view()


class ScheduledOperationWidget(zc.form.browser.combinationwidget.CombinationWidget):
    template = zope.app.pagetemplate.ViewPageTemplateFile('scheduled-operation-widget.pt')
    field_css_class = 'scheduled-operation-widget'

    def __call__(self):
        return self.template()


class ScheduledOperationSequenceWidget(zope.formlib.sequencewidget.TupleSequenceWidget):
    # Cannot use TupleSequenceWidget without this attribute
    field_css_class = ''


class ScheduledOperationsEdit(zeit.edit.browser.form.InlineForm):
    legend = _('')
    prefix = 'scheduled-operations'

    form_fields = zope.formlib.form.FormFields(
        zeit.workflow.scheduled.interfaces.IScheduledOperationsForm
    )

    def setUpWidgets(self, ignore_request=False):
        operations = self.form_fields['operations']
        operations.custom_widget = lambda field, request: (
            ScheduledOperationSequenceWidget(
                field,
                zeit.workflow.scheduled.interfaces.IScheduledOperationsForm['operations'],
                request,
                subwidget=ScheduledOperationWidget,
            )
        )

        ops_adapter = zeit.workflow.scheduled.interfaces.IScheduledOperations(self.context)
        operations = ops_adapter.list()

        data = {'operations': self._operations_to_form_data(operations)}

        self.widgets = zope.formlib.form.setUpDataWidgets(
            self.form_fields,
            self.prefix,
            self.context,
            self.request,
            data=data,
            ignore_request=ignore_request,
        )

    @zope.formlib.form.action(_('Apply'), condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        """Override to prevent default adapter-based data application."""
        self._success_handler(data)

    def _operations_to_form_data(self, operations):
        """Convert IScheduledOperation objects to tuple of tuples for the form."""
        result = []
        for op in operations:
            # Each operation is now a tuple: (id, scheduled_on, access, channels)
            # ID is hidden but tracked for updates
            access = op.property_changes.get('access')
            channels = op.property_changes.get('channels', ())

            result.append((op.id, op.scheduled_on, access, channels))

        return tuple(result)

    def _success_handler(self, data):
        if not data:
            return

        form_operations = data.get('operations', ())

        ops_adapter = zeit.workflow.scheduled.interfaces.IScheduledOperations(self.context)
        existing_ops = {op.id: op for op in ops_adapter.list()}
        form_op_ids = set()

        for form_op in form_operations:
            if not form_op or len(form_op) < 2:
                continue  # Skip invalid entries

            op_id = form_op[0]
            scheduled_on = form_op[1]
            access = form_op[2] if len(form_op) > 2 else None
            channels = form_op[3] if len(form_op) > 3 else ()

            # Validate scheduled_on is in future
            if scheduled_on and scheduled_on < pendulum.now('UTC'):
                continue  # Skip operations in the past

            property_changes = {}
            if access:
                property_changes['access'] = access
            if channels:
                property_changes['channels'] = channels

            try:
                if op_id and op_id in existing_ops:
                    ops_adapter.update(
                        op_id, scheduled_on=scheduled_on, property_changes=property_changes or None
                    )
                    form_op_ids.add(op_id)
                else:
                    new_id = ops_adapter.add('publish', scheduled_on, property_changes or None)
                    form_op_ids.add(new_id)
            except (ValueError, AttributeError, KeyError):
                continue  # Skip invalid operations

        for op_id in existing_ops:
            if op_id not in form_op_ids:
                try:
                    ops_adapter.remove(op_id)
                except KeyError:
                    pass  # Already removed
