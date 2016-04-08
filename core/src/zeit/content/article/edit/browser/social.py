from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.browser.form import FormFields
import zeit.content.article.interfaces
import zeit.edit.browser.form
import zeit.push.browser.form
import zope.formlib.form


class Container(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Social media')


class Social(zeit.push.browser.form.SocialBase,
             zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'social'
    undo_description = _('edit social media')

    FormFieldsFactory = FormFields
    form_fields = FormFieldsFactory()

    def __init__(self, context, request):
        super(Social, self).__init__(context, request)
        self.form_fields += self.FormFieldsFactory(
            zeit.content.article.interfaces.IArticle).select(
                'is_amp', 'is_instant_article')

    @zope.formlib.form.action(
        _('Apply'), condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        self.applyAccountData(self.context, data)
        super(Social, self).handle_edit_action.success(data)
