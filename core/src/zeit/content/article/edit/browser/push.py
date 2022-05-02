from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.browser.form import FormFields
import grokcore.component as grok
import zeit.content.article.interfaces
import zeit.edit.browser.form
import zeit.push.browser.form
import zope.interface
import zope.schema


class SocialContainer(zeit.edit.browser.form.FoldableFormGroup):

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
            zeit.content.article.interfaces.IArticle).select('is_amp')

    def setUpWidgets(self, *args, **kw):
        super(Social, self).setUpWidgets(*args, **kw)
        if self.context.access != 'free':
            self.widgets['is_amp'].extra = 'disabled="disabled"'


class MobileContainer(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Mobile apps')


class Mobile(zeit.push.browser.form.MobileBase,
             zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'mobile'
    undo_description = _('edit mobile apps')

    FormFieldsFactory = FormFields
    form_fields = FormFieldsFactory()

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super(Mobile, self).__call__()

    @property
    def mobile_form_fields(self):
        fields = self.FormFieldsFactory(IAuthorPush)
        fields['author_enabled'].custom_widget = HideOnFalseWidget
        fields += super(Mobile, self).mobile_form_fields
        return fields

    @zope.formlib.form.action(
        _('Apply'), condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        accountdata = zeit.push.interfaces.IAccountData(self.context)
        previous = accountdata.mobile_image
        super(Mobile, self).handle_edit_action.success(data)
        current = accountdata.mobile_image
        if current != previous:
            accountdata._set_mobile_service(image_set_manually=True)


class IAuthorPush(zope.interface.Interface):

    author_enabled = zope.schema.Bool(
        title=_('Author push enabled'),
        readonly=True)


@grok.implementer(IAuthorPush)
class AuthorPush(grok.Adapter):

    grok.context(zeit.content.article.interfaces.IArticle)

    # Should this move to zeit.push.interfaces.IAccountData?
    @property
    def author_enabled(self):
        push = zeit.push.interfaces.IPushMessages(self.context)
        service = push.get(type='mobile', variant='automatic-author')
        return service and service.get('enabled')


class HideOnFalseWidget(zope.formlib.widgets.DisplayWidget):

    def __call__(self):
        if self._data:
            return '<div class="output">%s</div>' % self._translate(
                self.context.title)
        else:
            return ''
