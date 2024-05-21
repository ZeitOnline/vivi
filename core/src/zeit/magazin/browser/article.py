import zope.interface

from zeit.content.article.edit.browser.form import FormFields
import zeit.cms.browser.interfaces
import zeit.edit.browser.form


class NextRead(zeit.edit.browser.form.InlineForm):
    legend = ''
    prefix = 'nextread'
    form_fields = FormFields(
        zeit.magazin.interfaces.INextRead, zeit.magazin.interfaces.IRelatedLayout
    )

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.widgets['nextread'].detail_view_name = '@@related-details'

    def __call__(self):
        zope.interface.alsoProvides(self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super().__call__()
