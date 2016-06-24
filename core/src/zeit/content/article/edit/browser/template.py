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
        'template', 'header_layout')

    def render(self):
        result = super(EditTemplate, self).render()
        if result:
            result += """\
<script type="text/javascript">
    zeit.cms.configure_master_slave(
        "%s.", "template", "header_layout",
        "@@zeit.content.article.update_articletemplate.json");
</script>""" % self.prefix
        return result

    def _success_handler(self):
        self.signal('reload-inline-form', 'article-content-main-image')
        self.reload(
            zeit.content.article.edit.interfaces.IHeaderArea(self.context))


class TemplateUpdater(
        zeit.cms.content.browser.widget.MasterSlaveDropdownUpdater):

    master_source = zeit.content.article.source.ArticleTemplateSource()
    slave_source = zeit.content.article.source.ArticleHeaderSource()
