from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zeit.cms.browser.interfaces
import zeit.cms.content.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.cp.interfaces
import zeit.objectlog.interfaces
import zeit.workflow.browser.form
import zope.component
import zope.dublincore.interfaces
import zope.formlib.form


def is_published_and_has_permission(form, action):
    return (zeit.workflow.browser.form.is_published(form, action) and
            form.request.interaction.checkPermission(
                'zeit.content.cp.Retract', form.context))


@zope.component.adapter(
    zeit.content.cp.interfaces.ICenterPage,
    zeit.cms.browser.interfaces.ICMSLayer)
class CenterPageWorkflowForm(zeit.workflow.browser.form.WorkflowForm):
    # same as zeit.workflow.browser.form.ContentWorkflow, except for the
    # fields: we use ITimeBasedPublishing instead of IContentWorkflow

    field_groups = (
        gocept.form.grouped.Fields(
            _("Status"),
            zeit.workflow.browser.form.WorkflowForm.modified_fields,
            css_class='column-left'),
        gocept.form.grouped.RemainingFields(
            _("Settings"), css_class='column-right'),
        gocept.form.grouped.Fields(
            _("Log"), fields=('logs', ),
            css_class='full-width')
    )

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.workflow.interfaces.ITimeBasedPublishing,
            zeit.objectlog.interfaces.ILog,
            zeit.cms.workflow.interfaces.IModified,
            zeit.cms.content.interfaces.ISemanticChange).omit(
                *zeit.workflow.browser.form.WorkflowForm.omit_fields) +
        zope.formlib.form.FormFields(
            zope.dublincore.interfaces.IDCTimes, for_display=True).select(
                'created'))

    @zope.formlib.form.action(_('Save state only'), name='save')
    def handle_save_state(self, action, data):
        """Duplicate action from base class, since we overwrite handle_retract.
        """
        super().handle_save_state.success(data)

    @zope.formlib.form.action(_('Save state and publish now'), name='publish')
    def handle_publish(self, action, data):
        """Duplicate action from base class, since we overwrite handle_retract.
        """
        super().handle_publish.success(data)

    @gocept.form.action.confirm(
        _('Save state and retract now'),
        name='retract',
        confirm_message=_('Really retract? This will remove the object from '
                          'all channels it is syndicated in and make it '
                          'unavailable to the public!'),
        condition=is_published_and_has_permission)
    def handle_retract(self, action, data):
        """Overwrite action to additionally test Retract permission."""
        super().handle_retract.success(data)

    def get_error_message(self, mapping):
        return _('Could not publish ${id} since it has validation errors.',
                 mapping=mapping)
