# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.formlib.form

import gocept.form.grouped

import zeit.objectlog.interfaces

import zeit.cms.browser.form
import zeit.cms.workflow.interfaces
import zeit.workflow.interfaces
from zeit.cms.i18n import MessageFactory as _


def is_published(form, action):
    return form.info.published


class WorkflowForm(zeit.cms.browser.form.EditForm):

    title = _("Workflow")

    field_groups = (
        gocept.form.grouped.Fields(
            _("Status"),
            ('last_modified_by', 'date_last_modified',
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
        zope.formlib.form.FormFields(zeit.workflow.interfaces.IWorkflowStatus)
        + zope.formlib.form.FormFields(zeit.objectlog.interfaces.ILog)
        + zope.formlib.form.FormFields(
            zeit.cms.workflow.interfaces.IModified))

    @zope.formlib.form.action(_('Save state only'))
    def handle_save_state(self, action, data):
        self.applyChanges(data)

    @zope.formlib.form.action(_('Save state and publish'))
    def handle_publish(self, action, data):
        self.applyChanges(data)
        mapping = dict(
            name=self.context.__name__,
            id=self.context.uniqueId)
        if self.info.can_publish():
            self.publish.publish()
            self.send_message(_('scheduled-for-publishing',
                                mapping=mapping))
        else:
            self.send_message(_('publish-preconditions-not-met',
                                mapping=mapping),
                              type='error')

    @zope.formlib.form.action(_('Save state and retract'),
                              condition=is_published)
    def handle_retract(self, action, data):
        self.applyChanges(data)
        mapping = dict(
            name=self.context.__name__,
            id=self.context.uniqueId)
        self.publish.retract()
        self.send_message(_('scheduled-for-retracting',
                            mapping=mapping))

    @property
    def publish(self):
        return zeit.cms.workflow.interfaces.IPublish(self.context)

    @property
    def info(self):
        return zeit.workflow.interfaces.IWorkflowStatus(self.context)
