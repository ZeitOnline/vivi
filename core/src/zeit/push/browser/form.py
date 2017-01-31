from zeit.cms.i18n import MessageFactory as _
from zeit.push.interfaces import facebookAccountSource, twitterAccountSource
import gocept.form.grouped
import zeit.cms.browser.form
import zeit.cms.testcontenttype.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zope.formlib.form


class SocialBase(zeit.cms.browser.form.CharlimitMixin):

    FormFieldsFactory = zope.formlib.form.FormFields

    social_fields = gocept.form.grouped.Fields(
        _("Social media"),
        ('facebook_main_text', 'facebook_main_enabled',
         'short_text', 'twitter_main_enabled',
         'twitter_ressort_enabled', 'twitter_ressort',
         'bigshare_buttons', 'mobile_text', 'mobile_enabled'),
        css_class='wide-widgets column-left')

    def __init__(self, *args, **kw):
        super(SocialBase, self).__init__(*args, **kw)
        self.form_fields += self.social_form_fields

    @property
    def social_form_fields(self):
        return (
            self.FormFieldsFactory(
                zeit.push.interfaces.IAccountData).select(
                    'facebook_main_text', 'facebook_main_enabled') +
            self.FormFieldsFactory(
                zeit.push.interfaces.IPushMessages).select('short_text') +
            self.FormFieldsFactory(
                zeit.push.interfaces.IAccountData).select(
                    'twitter_main_enabled',
                    'twitter_ressort_enabled', 'twitter_ressort') +
            self.FormFieldsFactory(
                zeit.cms.content.interfaces.ICommonMetadata).select(
                    'bigshare_buttons') +
            self.FormFieldsFactory(
                zeit.push.interfaces.IAccountData).select(
                    'mobile_text', 'mobile_enabled'))

    def setUpWidgets(self, *args, **kw):
        super(SocialBase, self).setUpWidgets(*args, **kw)
        self.set_charlimit('short_text')
        if self.request.form.get('%s.facebook_main_enabled' % self.prefix):
            self._set_widget_required('facebook_main_text')
        if self.request.form.get('%s.twitter_ressort_enabled' % self.prefix):
            self._set_widget_required('twitter_ressort')
        if self.request.form.get('%s.mobile_enabled' % self.prefix):
            self._set_widget_required('mobile_text')

    def _set_widget_required(self, name):
        field = self.widgets[name].context
        cloned = field.bind(field.context)
        cloned.required = True
        self.widgets[name].context = cloned

    def applyAccountData(self, object, data):
        # We cannot use the key ``text``, since the first positional parameter
        # of IPushNotifier.send() is also called text, which would result in a
        # TypeError.
        zeit.push.interfaces.IPushMessages(object).message_config = [
            {'type': 'facebook',
             'enabled': data.pop('facebook_main_enabled', False),
             'override_text': data.pop('facebook_main_text', None),
             'account': facebookAccountSource(None).MAIN_ACCOUNT},
            {'type': 'facebook',
             'enabled': data.pop('facebook_magazin_enabled', False),
             'override_text': data.pop('facebook_magazin_text', None),
             'account': facebookAccountSource(None).MAGAZIN_ACCOUNT},
            {'type': 'facebook',
             'enabled': data.pop('facebook_campus_enabled', False),
             'override_text': data.pop('facebook_campus_text', None),
             'account': facebookAccountSource(None).CAMPUS_ACCOUNT},
            {'type': 'twitter',
             'enabled': data.pop('twitter_main_enabled', False),
             'account': twitterAccountSource(None).MAIN_ACCOUNT},
            {'type': 'twitter',
             'enabled': data.pop('twitter_ressort_enabled', False),
             'account': data.pop('twitter_ressort', None)},
            {'type': 'mobile',
             'enabled': data.pop('mobile_enabled', False),
             'override_text': data.pop('mobile_text', None),
             'channels': zeit.push.interfaces.CONFIG_CHANNEL_NEWS},
        ]


class SocialAddForm(
        SocialBase, zeit.cms.content.browser.form.CommonMetadataAddForm):

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.testcontenttype.interfaces.IExampleContentType).omit(
            'authors', 'xml', 'bigshare_buttons')
    factory = zeit.cms.testcontenttype.testcontenttype.ExampleContentType

    field_groups = (
        zeit.cms.content.browser.form.CommonMetadataAddForm.field_groups +
        (SocialBase.social_fields,))

    def applyChanges(self, object, data):
        self.applyAccountData(object, data)
        return super(SocialAddForm, self).applyChanges(object, data)


class SocialEditForm(SocialBase, zeit.cms.browser.form.EditForm):

    form_fields = zope.formlib.form.FormFields()

    @zope.formlib.form.action(
        _('Apply'), condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        self.applyAccountData(self.context, data)
        super(SocialEditForm, self).handle_edit_action.success(data)
