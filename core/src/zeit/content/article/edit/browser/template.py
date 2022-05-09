from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.browser.form import FormFields
import zeit.cms.content.browser.widget
import zeit.content.article.source
import zeit.edit.browser.form


class EditTemplate(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'options-template'
    undo_description = _('edit options')
    form_fields = FormFields(
        zeit.content.article.interfaces.IArticle).select(
        'template', 'header_layout', 'header_color')

    def render(self):
        result = super().render()
        if result:
            result += """\
<script type="text/javascript">
    zeit.cms.configure_parent_child(
        "%s.", "template", "header_layout",
        "@@zeit.content.article.update_articletemplate.json", "header_color");
    zeit.cms.configure_parent_child(
        "%s.", "header_layout", "header_color",
        "@@zeit.content.article.update_articleheader.json");
</script>""" % (self.prefix, self.prefix)
        return result

    def _success_handler(self):
        self.signal('reload-inline-form', 'article-content-main-image')
        self.reload(self.context.header)


class TemplateUpdater(
        zeit.cms.content.browser.widget.ParentChildDropdownUpdater):

    parent_source = zeit.content.article.source.ArticleTemplateSource()
    child_source = zeit.content.article.source.ArticleHeaderSource()


class HeaderUpdater(
        zeit.cms.content.browser.widget.ParentChildDropdownUpdater):

    parent_source = zeit.content.article.source.ArticleHeaderSource()
    child_source = zeit.content.article.source.ArticleHeaderColorSource()
