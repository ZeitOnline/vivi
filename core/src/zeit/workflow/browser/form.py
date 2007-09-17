# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.formlib.form

import zeit.cms.browser.form


class WorkflowForm(zeit.cms.browser.form.EditForm):

    form_fields = zope.formlib.form.Fields(
        zeit.workflow.interfaces.IWorkflow,
        render_context=True, omit_readonly=False)
