from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import grokcore.component as grok
import zeit.cms.browser.interfaces
import zeit.newsletter.interfaces
import zeit.workflow.browser.form
import zope.formlib.form


class Form(zeit.workflow.browser.form.WorkflowForm, grok.MultiAdapter):

    grok.adapts(
        zeit.newsletter.interfaces.INewsletter,
        zeit.cms.browser.interfaces.ICMSLayer)
    grok.provides(zeit.workflow.browser.interfaces.IWorkflowForm)

    field_groups = (
        gocept.form.grouped.Fields(
            _("Status"),
            ('last_modified_by', 'date_last_modified', 'last_semantic_change',
             'created',
             'published', 'date_last_published', 'date_first_released'),
            css_class='column-left'),
        gocept.form.grouped.RemainingFields(
            _("Settings"), css_class='column-right'),
        gocept.form.grouped.Fields(
            _("Log"), fields=('logs', ),
            css_class='full-width')
    )

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.newsletter.interfaces.INewsletterWorkflow,
            zeit.objectlog.interfaces.ILog,
            zeit.cms.workflow.interfaces.IModified,
            zeit.cms.content.interfaces.ISemanticChange).omit(
                'has_semantic_change', 'date_print_published',
                'error_messages') +
        zope.formlib.form.FormFields(
            zope.dublincore.interfaces.IDCTimes, for_display=True).select(
                'created') +
        zope.formlib.form.FormFields(
            zeit.newsletter.interfaces.ITestRecipient)
    )

    @property
    def adapters(self):
        # XXX Dear formlib, it would be really nice if you'd let subclasses
        # override self.adapters, and not set it to {} first thing in every
        # setUpWidgets call.
        return self._adapters

    @adapters.setter
    def adapters(self, value):
        pass  # ignored, see above

    def setUpWidgets(self, ignore_request=False):
        # determining the test recipient doesn't actually have to do anything
        # with our context (the newsletter), so we cheat and inject a
        # pseudo-adapter that is callable with a context, but implements
        # ITestRecipient all by itself
        recipient = zeit.newsletter.interfaces.ITestRecipient(self.request)
        self._adapters = {
            zeit.newsletter.interfaces.ITestRecipient: recipient,
        }
        super().setUpWidgets(ignore_request)

    # override from baseclass to change the title
    @zope.formlib.form.action(_('Send emails and publish now'),
                              name='publish')
    def handle_publish(self, action, data):
        return super().handle_publish.success_handler(
            self, action, data)

    # once you override one action, you don't get any action from your base
    # class anymore
    @zope.formlib.form.action(_('Save state only'),
                              name='save')
    def handle_save_state(self, action, data):
        return super().handle_save_state.success_handler(
            self, action, data)

    @zope.formlib.form.action(_('Test email'),
                              name='test')
    def handle_test(self, action, data):
        super().handle_edit_action.success(data)
        recipient = zeit.newsletter.interfaces.ITestRecipient(self.request)
        self.context.send_test(recipient.email)
