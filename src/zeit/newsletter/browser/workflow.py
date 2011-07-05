# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import grokcore.component as grok
import zeit.cms.browser.interfaces
import zeit.newsletter.interfaces
import zeit.workflow.browser.form
import zope.component
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
            zeit.cms.content.interfaces.ISemanticChange) +
        zope.formlib.form.FormFields(
            zope.dublincore.interfaces.IDCTimes, for_display=True).select(
                'created'))

    @zope.formlib.form.action(_('Save state only'),
                              name='save',
                              condition=lambda *args: False)
    def handle_save_state(self, action, data):
        pass # we dont't have any state to save

    @zope.formlib.form.action(_('Send emails and publish now'),
                              name='publish')
    def handle_publish(self, action, data):
        return super(Form, self).handle_publish.success_handler(
            self, action, data)
