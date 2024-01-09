import zope.component

import zeit.cms.browser.interfaces
import zeit.content.article.interfaces
import zeit.workflow.browser.form


@zope.component.adapter(
    zeit.content.article.interfaces.IArticle, zeit.cms.browser.interfaces.ICMSLayer
)
class ArticleWorkflowForm(zeit.workflow.browser.form.ContentWorkflow):
    form_fields = zeit.workflow.browser.form.ContentWorkflow.form_fields
