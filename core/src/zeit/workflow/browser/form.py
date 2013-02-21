# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
"""Workflow forms."""

import zope.component
import zope.dublincore.interfaces
import zope.interface
import zope.formlib.form

import gocept.form.action
import gocept.form.grouped

import zeit.objectlog.interfaces

import zeit.cms.browser.form
import zeit.cms.browser.interfaces
import zeit.cms.workflow.interfaces
import zeit.workflow.interfaces
import zeit.workflow.browser.interfaces
from zeit.cms.i18n import MessageFactory as _


def is_published(form, action):
    return form.info.published


def workflow_form_factory(context, request):
    return zope.component.queryMultiAdapter(
        (context, request),
        zeit.workflow.browser.interfaces.IWorkflowForm)


class WorkflowActions(object):

    def do_publish(self):
        mapping = dict(
            name=self.context.__name__,
            id=self.context.uniqueId)
        if self.info.can_publish():
            self.publish.publish()
            self.send_message(
                _('scheduled-for-immediate-publishing',
                  default=u"${id} has been scheduled for publishing.",
                  mapping=mapping))
        else:
            self.send_message(self.get_error_message(mapping), type='error')

    def do_retract(self):
        mapping = dict(
            name=self.context.__name__,
            id=self.context.uniqueId)
        self.publish.retract()
        self.send_message(
            _('scheduled-for-immediate-retracting',
              default=u"${id} has been scheduled for retracting.",
              mapping=mapping))

    def get_error_message(self, mapping):
        return _('publish-preconditions-not-met', mapping=mapping)

    @property
    def publish(self):
        return zeit.cms.workflow.interfaces.IPublish(self.context)

    @property
    def info(self):
        return zeit.cms.workflow.interfaces.IPublishInfo(self.context)


class WorkflowForm(zeit.cms.browser.form.EditForm, WorkflowActions):

    zope.interface.implements(zeit.workflow.browser.interfaces.IWorkflowForm)

    title = _("Workflow")

    @zope.formlib.form.action(_('Save state only'),
                              name='save')
    def handle_save_state(self, action, data):
        self.applyChanges(data)

    @zope.formlib.form.action(_('Save state and publish now'),
                              name='publish')
    def handle_publish(self, action, data):
        self.applyChanges(data)
        self.do_publish()

    @gocept.form.action.confirm(
        _('Save state and retract now'),
        name='retract',
        confirm_message=_('Really retract? This will remove the object from '
                          'all channels it is syndicated in and make it '
                          'unavailable to the public!'),
        condition=is_published)
    def handle_retract(self, action, data):
        self.applyChanges(data)
        self.do_retract()


class ContentWorkflow(WorkflowForm):

    zope.component.adapts(
        zeit.cms.interfaces.IEditorialContent,
        zeit.cms.browser.interfaces.ICMSLayer)

    field_groups = (
        gocept.form.grouped.Fields(
            _("Status"),
            ('last_modified_by', 'date_last_modified', 'last_semantic_change',
             'created',
             'published', 'date_last_published', 'date_first_released',
             'edited', 'corrected', 'refined', 'images_added'),
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
            'has_semantic_change') +
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
            ('last_modified_by', 'date_last_modified', 'last_semantic_change',
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
            zeit.workflow.interfaces.IAssetWorkflow,
            zeit.objectlog.interfaces.ILog,
            zeit.cms.workflow.interfaces.IModified,
            zeit.cms.content.interfaces.ISemanticChange).omit(
            'has_semantic_change'))


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
