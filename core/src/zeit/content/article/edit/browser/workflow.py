from unittest import mock

from zope.cachedescriptors.property import Lazy as cachedproperty
import pendulum
import zope.app.pagetemplate
import zope.component
import zope.formlib.form
import zope.formlib.interfaces
import zope.formlib.sequencewidget
import zope.formlib.widget
import zope.i18n

from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.repository.interfaces import IAutomaticallyRenameable
import zeit.content.article.interfaces
import zeit.edit.browser.form
import zeit.workflow.interfaces


class WorkflowTimeContainer(zeit.edit.browser.form.FoldableFormGroup):
    title = _('Workflow time')


class Timebased(zeit.edit.browser.form.InlineForm):
    legend = _('Article')
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


class ScheduledOperationFormBase(
    zeit.edit.browser.form.InlineForm, zeit.cms.browser.form.WidgetCSSMixin
):
    property_key = NotImplemented
    property_default = None
    display_only = False

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._operation_id = None
        # Store partial input that hasn't been saved yet
        self._pending_data = None

    def render(self):
        if not FEATURE_TOGGLES.find('use_scheduled_operations'):
            return ''
        return super().render()

    def get_data(self):
        if self._pending_data is not None:
            return self._pending_data

        ops = zeit.workflow.scheduled.interfaces.IScheduledOperations(self.context)
        operation = self._find_operation(ops.list('publish'))
        self._operation_id = operation.id if operation else None

        return {
            'scheduled_on': operation.scheduled_on if operation else None,
            self.property_key: (
                operation.property_changes.get(self.property_key, self.property_default)
                if operation
                else self.property_default
            ),
        }

    def setUpWidgets(self, ignore_request=False):
        self.widgets = zope.formlib.form.setUpDataWidgets(
            self.form_fields,
            self.prefix,
            self.context,
            self.request,
            data=self.get_data(),
            for_display=self.display_only,
            ignore_request=ignore_request,
        )

        # XXX copy&paste from WidgetCSSMixin since we're skipping super()
        for widget in self.widgets:
            widget.field_css_class = self._assemble_css_classes.__get__(widget)

    def _find_operation(self, operations):
        for op in operations:
            if self.property_key in op.property_changes:
                return op
        return None

    @zope.formlib.form.action(_('Apply'), condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        self._success_handler(data)

    def _success_handler(self, data):
        if not FEATURE_TOGGLES.find('use_scheduled_operations'):
            return

        if not data:
            return

        ops = zeit.workflow.scheduled.interfaces.IScheduledOperations(self.context)
        scheduled_on = data.get('scheduled_on')
        property_value = data.get(self.property_key)

        has_scheduled_on = scheduled_on and scheduled_on >= pendulum.now('UTC')
        has_property_value = property_value and property_value != self.property_default

        if not scheduled_on:
            if self._operation_id:
                try:
                    ops.remove(self._operation_id)
                    self._operation_id = None
                except KeyError:
                    pass
            self._pending_data = {
                'scheduled_on': scheduled_on,
                self.property_key: property_value if property_value else self.property_default,
            }
        elif has_scheduled_on and has_property_value:
            self._create_or_update_operation(ops, scheduled_on, property_value)
            self._pending_data = None
        else:
            self._pending_data = {
                'scheduled_on': scheduled_on,
                self.property_key: property_value if property_value else self.property_default,
            }

    def _create_or_update_operation(self, ops, scheduled_on, property_value):
        property_changes = {self.property_key: property_value}
        try:
            if self._operation_id:
                ops.update(
                    self._operation_id, scheduled_on=scheduled_on, property_changes=property_changes
                )
            else:
                self._operation_id = ops.add('publish', scheduled_on, property_changes)
        except (ValueError, AttributeError, KeyError):
            pass


class ScheduledAccessOperation(ScheduledOperationFormBase):
    legend = _('Access')
    prefix = 'scheduled-access-operation'
    css_class = 'scheduled-operation'
    property_key = 'access'

    form_fields = zope.formlib.form.FormFields(
        zeit.workflow.scheduled.interfaces.IScheduledAccessOperation
    )
    form_fields['scheduled_on'].field.required = False


class ScheduledChannelOperation(ScheduledOperationFormBase):
    legend = _('Channel')
    prefix = 'scheduled-channel-operation'
    css_class = 'scheduled-operation'
    property_key = 'channels'
    property_default = ()

    form_fields = zope.formlib.form.FormFields(
        zeit.workflow.scheduled.interfaces.IScheduledChannelOperation
    )
    form_fields['scheduled_on'].field.required = False

    def render(self):
        """Copied from class ChannelSelector"""
        if not FEATURE_TOGGLES.find('use_scheduled_operations'):
            return ''
        result = super().render()
        if result:
            result += """\
<script type="text/javascript">
    zeit.cms.configure_channel_dropdowns("%s.", "channels", "00", "01");
</script>""" % (self.prefix,)
        return result
