from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.browser.form import FormFields
import zeit.content.article.interfaces
import zeit.edit.browser.form
import zeit.push.browser.form
import zope.interface


class SocialContainer(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Social media')


class Social(zeit.push.browser.form.SocialBase,
             zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'social'
    undo_description = _('edit social media')

    FormFieldsFactory = FormFields
    form_fields = FormFieldsFactory()


class MobileContainer(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Mobile apps')


class Mobile(zeit.push.browser.form.MobileBase,
             zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'mobile'
    undo_description = _('edit mobile apps')

    FormFieldsFactory = FormFields
    form_fields = FormFieldsFactory()

    def __init__(self, context, request):
        super(Mobile, self).__init__(context, request)
        self.form_fields += self.FormFieldsFactory(
            zeit.content.article.interfaces.IArticle).select(
                'is_amp', 'is_instant_article')

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super(Mobile, self).__call__()

    def setUpWidgets(self, *args, **kw):
        super(Mobile, self).setUpWidgets(*args, **kw)
        if self.context.access != u'free':
            self.widgets['is_amp'].extra = 'disabled="disabled"'
            self.widgets['is_instant_article'].extra = 'disabled="disabled"'

    @zope.formlib.form.action(
        _('Apply'), condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        accountdata = zeit.push.interfaces.IAccountData(self.context)
        previous = accountdata.mobile_image
        super(Mobile, self).handle_edit_action.success(data)
        current = accountdata.mobile_image
        if current != previous:
            push = zeit.push.interfaces.IPushMessages(self.context)
            push.set({'type': 'mobile'}, image_set_manually=True)
