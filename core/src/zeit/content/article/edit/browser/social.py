from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.browser.form import FormFields
import zeit.edit.browser.form
import zeit.push.browser.form


class Container(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Social media')


class Social(zeit.push.browser.form.SocialBase,
             zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'social'
    undo_description = _('edit social media')

    FormFieldsFactory = FormFields
    form_fields = FormFieldsFactory()

    def applyChanges(self, data):
        self.applyAccountData(self.context, data)
        return super(Social, self).applyChanges(data)
