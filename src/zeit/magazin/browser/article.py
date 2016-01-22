from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.browser.form import FormFields
import zeit.cms.browser.interfaces
import zeit.content.article.edit.browser.social
import zeit.edit.browser.form
import zeit.magazin.browser.social
import zope.interface


class NextRead(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'nextread'
    undo_description = _('edit internal links')
    form_fields = FormFields(
        zeit.magazin.interfaces.INextRead,
        zeit.magazin.interfaces.IRelatedLayout)

    def setUpWidgets(self, *args, **kw):
        super(NextRead, self).setUpWidgets(*args, **kw)
        self.widgets['nextread'].detail_view_name = '@@related-details'

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super(NextRead, self).__call__()


class Social(zeit.content.article.edit.browser.social.Social,
             zeit.magazin.browser.social.SocialBase):
    pass
