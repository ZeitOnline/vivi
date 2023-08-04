from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.browser.form import FormFields
import zeit.content.article.edit.browser.push
import zeit.edit.browser.form
import zeit.magazin.browser.social


class NextRead(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'nextread'
    undo_description = _('edit internal links')
    form_fields = FormFields(
        zeit.magazin.interfaces.INextRead,
        zeit.magazin.interfaces.IRelatedLayout)

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.widgets['nextread'].detail_view_name = '@@related-details'


class Social(zeit.content.article.edit.browser.push.Social,
             zeit.magazin.browser.social.SocialBase):
    pass
