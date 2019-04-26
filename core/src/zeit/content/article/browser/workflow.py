import zeit.cms.browser.interfaces
import zeit.content.article.interfaces
import zeit.workflow.browser.form
import zope.component


class ArticleWorkflowForm(zeit.workflow.browser.form.ContentWorkflow):

    zope.component.adapts(
        zeit.content.article.interfaces.IArticle,
        zeit.cms.browser.interfaces.ICMSLayer)

    form_fields = zeit.workflow.browser.form.ContentWorkflow.form_fields
