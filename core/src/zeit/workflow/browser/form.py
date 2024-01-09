from zope.cachedescriptors.property import Lazy as cachedproperty
import gocept.form.action
import gocept.form.grouped
import zope.component
import zope.dublincore.interfaces
import zope.formlib.form
import zope.interface

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import CAN_PUBLISH_SUCCESS, CAN_RETRACT_SUCCESS
import zeit.cms.browser.form
import zeit.cms.browser.interfaces
import zeit.cms.workflow.interfaces
import zeit.objectlog.interfaces
import zeit.workflow.browser.interfaces
import zeit.workflow.interfaces


def is_published(form, action):
    return form.info.published


def workflow_form_factory(context, request):
    return zope.component.queryMultiAdapter(
        (context, request), zeit.workflow.browser.interfaces.IWorkflowForm
    )


class WorkflowActions:
    def do_publish(self):
        if self.info.can_publish() == CAN_PUBLISH_SUCCESS:
            # XXX Work around race condition between celery/redis (applies
            # already in tpc_vote) and DAV-cache in ZODB (applies only in
            # tpc_finish, so the celery job *may* start executing before that
            # happend), see BUG-796.
            self.publish.publish(countdown=5)
            self.send_message(
                _(
                    'scheduled-for-immediate-publishing',
                    default='${id} has been scheduled for publishing.',
                    mapping=self._error_mapping,
                )
            )
        else:
            self.send_validation_messages()

    def do_retract(self):
        if self.info.can_retract() == CAN_RETRACT_SUCCESS:
            self.publish.retract(countdown=5)
            self.send_message(
                _(
                    'scheduled-for-immediate-retracting',
                    default='${id} has been scheduled for retracting.',
                    mapping=self._error_mapping,
                )
            )
        else:
            self.send_validation_messages()

    def send_validation_messages(self):
        self.send_message(
            _(
                'publish-preconditions-not-met',
                default='${id} cannot be published.',
                mapping=self._error_mapping,
            ),
            type='error',
        )
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


@zope.interface.implementer(zeit.workflow.browser.interfaces.IWorkflowForm)
class WorkflowForm(zeit.cms.browser.form.EditForm, WorkflowActions):
    title = _('Workflow')

    modified_fields = (
        'last_modified_by',
        'date_last_modified',
        'last_semantic_change',
        'date_last_checkout',
        'created',
        'published',
        'date_last_published',
        'last_published_by',
        'date_last_published_semantic',
        'date_first_released',
    )

    omit_fields = ('date_print_published', 'error_messages')

    @zope.formlib.form.action(_('Save state only'), name='save')
    def handle_save_state(self, action, data):
        super().handle_edit_action.success(data)

    @zope.formlib.form.action(_('Save state and publish now'), name='publish')
    def handle_publish(self, action, data):
        super().handle_edit_action.success(data)
        self.do_publish()

    @gocept.form.action.confirm(
        _('Save state and retract now'),
        name='retract',
        confirm_message=_(
            'Really retract? This will remove the object from '
            'all channels it is syndicated in and make it '
            'unavailable to the public!'
        ),
        condition=is_published,
    )
    def handle_retract(self, action, data):
        super().handle_edit_action.success(data)
        self.do_retract()


@zope.component.adapter(
    zeit.cms.interfaces.IEditorialContent, zeit.cms.browser.interfaces.ICMSLayer
)
class ContentWorkflow(WorkflowForm):
    field_groups = (
        gocept.form.grouped.Fields(
            _('Status'),
            WorkflowForm.modified_fields + ('edited', 'corrected', 'seo_optimized'),
            css_class='column-left',
        ),
        gocept.form.grouped.RemainingFields(_('Settings'), css_class='column-right'),
        gocept.form.grouped.Fields(
            _('Publish lock?'),
            (
                'locked',
                'lock_reason',
            ),
            css_class='column-right',
        ),
        gocept.form.grouped.Fields(_('Log'), fields=('logs',), css_class='full-width'),
    )

    form_fields = zope.formlib.form.FormFields(
        zeit.workflow.interfaces.IContentWorkflow,
        zeit.objectlog.interfaces.ILog,
        zeit.cms.workflow.interfaces.IModified,
        zeit.cms.content.interfaces.ISemanticChange,
    ).omit(*WorkflowForm.omit_fields) + zope.formlib.form.FormFields(
        zope.dublincore.interfaces.IDCTimes, for_display=True
    ).select('created')


@zope.component.adapter(zeit.cms.interfaces.IAsset, zeit.cms.browser.interfaces.ICMSLayer)
class AssetWorkflow(WorkflowForm):
    field_groups = (
        gocept.form.grouped.Fields(
            _('Status'), WorkflowForm.modified_fields, css_class='column-left'
        ),
        gocept.form.grouped.RemainingFields(_('Settings'), css_class='column-right'),
        gocept.form.grouped.Fields(
            _('Publish lock?'),
            (
                'locked',
                'lock_reason',
            ),
            css_class='column-right',
        ),
        gocept.form.grouped.Fields(_('Log'), fields=('logs',), css_class='full-width'),
    )

    form_fields = zope.formlib.form.FormFields(
        zeit.workflow.interfaces.IAssetWorkflow,
        zeit.objectlog.interfaces.ILog,
        zeit.cms.workflow.interfaces.IModified,
        zeit.cms.content.interfaces.ISemanticChange,
    ).omit(*WorkflowForm.omit_fields)


@zope.component.adapter(zeit.cms.interfaces.ICMSContent, zeit.cms.browser.interfaces.ICMSLayer)
@zope.interface.implementer(zeit.workflow.browser.interfaces.IWorkflowForm)
class NoWorkflow(zeit.cms.browser.form.EditForm):
    field_groups = (
        gocept.form.grouped.Fields(
            _('Status'), ('last_modified_by', 'date_last_modified'), css_class='full-width'
        ),
        gocept.form.grouped.Fields(_('Log'), fields=('logs',), css_class='full-width'),
    )

    form_fields = zope.formlib.form.FormFields(
        zeit.objectlog.interfaces.ILog, zeit.cms.workflow.interfaces.IModified
    )
