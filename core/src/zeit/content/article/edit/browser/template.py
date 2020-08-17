from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.browser.form import FormFields
import zeit.cms.content.browser.widget
import zeit.content.article.source
import zeit.edit.browser.form
import zope.interface


class EditTemplate(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'options-template'
    undo_description = _('edit options')
    form_fields = FormFields(
        zeit.content.article.interfaces.IArticle).select(
        'template', 'header_layout', 'header_color')

    def render(self):
        result = super(EditTemplate, self).render()
        if result:
            result += """\
<script type="text/javascript">
    zeit.cms.configure_master_slave(
        "%s.", "template", "header_layout",
        "@@zeit.content.article.update_articletemplate.json");
    zeit.cms.configure_master_slave(
        "%s.", "template", "header_color",
        "@@zeit.content.article.update_articleheader.json");
</script>""" % (self.prefix, self.prefix)
        return result

    def _success_handler(self):
        self.signal('reload-inline-form', 'article-content-main-image')
        self.reload(self.context.header)


class TemplateUpdater(
        zeit.cms.content.browser.widget.MasterSlaveDropdownUpdater):

    master_source = zeit.content.article.source.ArticleTemplateSource()
    slave_source = zeit.content.article.source.ArticleHeaderSource()


class HeaderUpdater(
        zeit.cms.content.browser.widget.MasterSlaveDropdownUpdater):

    master_source = zeit.content.article.source.ArticleTemplateSource()
    slave_source = zeit.content.article.source.ArticleHeaderColorSource()

    def get_result(self, master_token):
        try:
            master_value = self.master_terms.getValue(master_token)
        except KeyError:
            return []

        @zope.interface.implementer(
            self.slave_source.factory.master_value_iface)
        class Fake(object):
            pass
        fake = Fake()
        setattr(fake, self.slave_source.factory.master_value_key, master_value)

        source = self.slave_source(fake)
        terms = zope.component.getMultiAdapter(
            (source, self.request), zope.app.form.browser.interfaces.ITerms)
        result = []
        for value in source:
            term = terms.getTerm(value)
            result.append((term.title, term.token))

        return sorted(result)
