# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.interfaces
import zeit.content.article.interfaces
import zeit.workflow.browser.form
import zope.formlib.form


class ArticleWorkflowForm(zeit.workflow.browser.form.ContentWorkflow):

    zope.component.adapts(
        zeit.content.article.interfaces.IArticle,
        zeit.cms.browser.interfaces.ICMSLayer)

    form_fields = (
        zeit.workflow.browser.form.ContentWorkflow.form_fields
        + zope.formlib.form.FormFields(
            zeit.content.article.interfaces.ICDSWorkflow))
