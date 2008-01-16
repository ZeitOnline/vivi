# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.formlib.form

import zeit.cms.browser.form

_ = zope.i18nmessageid.MessageFactory('zeit.cms')

class WorkflowForm(zeit.cms.browser.form.EditForm):

    title = _("Workflow")

    widget_groups = (
        (_(u"Status"), (
            'published', 'edited', 'corrected', 'refined', 'images_added'),
         'column-left'),
        (_(u"Einstellung"), zeit.cms.browser.form.REMAINING_FIELDS,
         'column-right')
    )

    form_fields = zope.formlib.form.Fields(
        zeit.workflow.interfaces.IWorkflow,
        render_context=True, omit_readonly=False)
