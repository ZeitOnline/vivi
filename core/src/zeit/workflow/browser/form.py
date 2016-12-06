from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
from zeit.cms.workflow.interfaces import CAN_PUBLISH_SUCCESS
from zope.cachedescriptors.property import Lazy as cachedproperty
import gocept.form.action
import gocept.form.grouped
import zeit.cms.browser.form
import zeit.cms.browser.interfaces
import zeit.cms.workflow.interfaces
import zeit.objectlog.interfaces
import zeit.workflow.browser.interfaces
import zeit.workflow.interfaces
import zope.component
import zope.dublincore.interfaces
import zope.formlib.form
import zope.interface


def is_published(form, action):
    return form.info.published


def workflow_form_factory(context, request):
    return zope.component.queryMultiAdapter(
        (context, request),
        zeit.workflow.browser.interfaces.IWorkflowForm)


class WorkflowActions(object):

    def do_publish(self):
        if self.info.can_publish() == CAN_PUBLISH_SUCCESS:
            self.publish.publish()
            self.send_message(
                _('scheduled-for-immediate-publishing',
                  default=u"${id} has been scheduled for publishing.",
                  mapping=self._error_mapping))
        else:
            self.send_validation_messages()

    def do_retract(self):
        self.publish.retract()
        self.send_message(
            _('scheduled-for-immediate-retracting',
              default=u"${id} has been scheduled for retracting.",
              mapping=self._error_mapping))

    def send_validation_messages(self):
        self.send_message(
            _('publish-preconditions-not-met',
              default=u"${id} cannot be published.",
              mapping=self._error_mapping), type='error')
        for message in self.info.error_messages:
            self.send_message(message, type='error')

    @property
    def publish(self):
        return zeit.cms.workflow.interfaces.IPublish(self.context)

    @cachedproperty
    def info(self):
        return zeit.cms.workflow.interfaces.IPublishInfo(self.context)

    @property
    def _error_mapping(self):
        return {
            'name': self.context.__name__,
            'id': self.context.uniqueId,
        }


class WorkflowForm(zeit.cms.browser.form.EditForm, WorkflowActions):

    zope.interface.implements(zeit.workflow.browser.interfaces.IWorkflowForm)

    title = _("Workflow")

    modified_fields = (
        'last_modified_by', 'date_last_modified', 'last_semantic_change',
        'date_last_checkout',
        'created',
        'published',
        'date_last_published', 'last_published_by',
        'date_last_published_semantic', 'date_first_released'
    )

    omit_fields = (
        'date_print_published',
        'error_messages'
    )

    @zope.formlib.form.action(_('Save state only'),
                              name='save')
    def handle_save_state(self, action, data):
        super(WorkflowForm, self).handle_edit_action.success(data)

    @zope.formlib.form.action(_('Save state and publish now'),
                              name='publish')
    def handle_publish(self, action, data):
        super(WorkflowForm, self).handle_edit_action.success(data)
        self.do_publish()

    @gocept.form.action.confirm(
        _('Save state and retract now'),
        name='retract',
        confirm_message=_('Really retract? This will remove the object from '
                          'all channels it is syndicated in and make it '
                          'unavailable to the public!'),
        condition=is_published)
    def handle_retract(self, action, data):
        super(WorkflowForm, self).handle_edit_action.success(data)
        self.do_retract()


class ContentWorkflow(WorkflowForm):

    zope.component.adapts(
        zeit.cms.interfaces.IEditorialContent,
        zeit.cms.browser.interfaces.ICMSLayer)

    field_groups = (
        gocept.form.grouped.Fields(
            _("Status"),
            WorkflowForm.modified_fields + (
                'edited', 'corrected', 'refined',
                'images_added', 'seo_optimized'),
            css_class='column-left'),
        gocept.form.grouped.RemainingFields(
            _("Settings"), css_class='column-right'),
        gocept.form.grouped.Fields(
            _("Log"), fields=('logs', ),
            css_class='full-width')
    )

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.workflow.interfaces.IContentWorkflow,
            zeit.objectlog.interfaces.ILog,
            zeit.cms.workflow.interfaces.IModified,
            zeit.cms.content.interfaces.ISemanticChange).omit(
                *WorkflowForm.omit_fields) +
        zope.formlib.form.FormFields(
            zope.dublincore.interfaces.IDCTimes, for_display=True).select(
                'created'))


class AssetWorkflow(WorkflowForm):

    zope.component.adapts(
        zeit.cms.interfaces.IAsset,
        zeit.cms.browser.interfaces.ICMSLayer)

    field_groups = (
        gocept.form.grouped.Fields(
            _("Status"),
            WorkflowForm.modified_fields,
            css_class='column-left'),
        gocept.form.grouped.RemainingFields(
            _("Settings"), css_class='column-right'),
        gocept.form.grouped.Fields(
            _("Log"), fields=('logs', ),
            css_class='full-width')
    )

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.workflow.interfaces.IAssetWorkflow,
            zeit.objectlog.interfaces.ILog,
            zeit.cms.workflow.interfaces.IModified,
            zeit.cms.content.interfaces.ISemanticChange).omit(
                *WorkflowForm.omit_fields))


class NoWorkflow(zeit.cms.browser.form.EditForm):

    zope.interface.implements(zeit.workflow.browser.interfaces.IWorkflowForm)

    zope.component.adapts(
        zeit.cms.interfaces.ICMSContent,
        zeit.cms.browser.interfaces.ICMSLayer)

    field_groups = (
        gocept.form.grouped.Fields(
            _("Status"),
            ('last_modified_by', 'date_last_modified'),
            css_class='full-width'),
        gocept.form.grouped.Fields(
            _("Log"), fields=('logs', ),
            css_class='full-width')
    )

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.objectlog.interfaces.ILog,
            zeit.cms.workflow.interfaces.IModified))
