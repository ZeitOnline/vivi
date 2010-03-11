# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
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


class CenterPageWorkflowForm(zeit.workflow.browser.form.WorkflowForm):
    # same as zeit.workflow.browser.form.ContentWorkflow, except for the
    # fields: we use only ICenterPageWorkflow (which doesn't add anything to
    # ITimeBasedPublishing) instead of
    # zeit.workflow.interfaces.IContentWorkflow

    zope.component.adapts(
        zeit.content.cp.interfaces.ICenterPage,
        zeit.cms.browser.interfaces.ICMSLayer)

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
            zeit.content.cp.interfaces.IValidatingWorkflow,
            zeit.objectlog.interfaces.ILog,
            zeit.cms.workflow.interfaces.IModified,
            zeit.cms.content.interfaces.ISemanticChange) +
        zope.formlib.form.FormFields(
            zope.dublincore.interfaces.IDCTimes, for_display=True).select(
                'created'))

    def get_error_message(self, mapping):
        return _('Could not publish ${id} since it has validation errors.',
                 mapping=mapping)

