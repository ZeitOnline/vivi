from zeit.cms.i18n import MessageFactory as _
from zeit.push.facebook import facebookAccountSource
from zeit.push.twitter import twitterAccountSource
import gocept.form.grouped
import grokcore.component as grok
import zeit.cms.browser.form
import zeit.cms.testcontenttype.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zope.formlib.form
import zope.interface
import zope.schema


class IAccounts(zope.interface.Interface):

    facebook_main_enabled = zope.schema.Bool(title=_('Enable Facebook'))
    facebook_magazin_enabled = zope.schema.Bool(
        title=_('Enable Facebook Magazin'))
    twitter_main_enabled = zope.schema.Bool(title=_('Enable Twitter'))
    twitter_ressort_enabled = zope.schema.Bool(
        title=_('Enable Twitter Ressort'))
    twitter_ressort = zope.schema.Choice(
        title=_('Additional Twitter'),
        source=twitterAccountSource,
        required=False)
    mobile_text = zope.schema.TextLine(title=_('Mobile title'), required=False)
    mobile_enabled = zope.schema.Bool(title=_('Enable mobile push'))


class SocialBase(zeit.cms.browser.form.CharlimitMixin):

    FormFieldsFactory = zope.formlib.form.FormFields

    social_fields = gocept.form.grouped.Fields(
        _("Social media"),
        ('long_text', 'facebook_main_enabled', 'facebook_magazin_enabled',
         'short_text', 'twitter_main_enabled',
         'twitter_ressort_enabled', 'twitter_ressort',
         'mobile_text', 'mobile_enabled'),
        css_class='wide-widgets column-left')

    def __init__(self, *args, **kw):
        super(SocialBase, self).__init__(*args, **kw)
        self.form_fields += (
            self.FormFieldsFactory(
                zeit.push.interfaces.IPushMessages).select('long_text')
            + self.FormFieldsFactory(
                IAccounts).select(
                    'facebook_main_enabled', 'facebook_magazin_enabled')
            + self.FormFieldsFactory(
                zeit.push.interfaces.IPushMessages).select('short_text')
            + self.FormFieldsFactory(
                IAccounts).select(
                    'twitter_main_enabled',
                    'twitter_ressort_enabled', 'twitter_ressort')
            + self.FormFieldsFactory(
                IAccounts).select('mobile_text', 'mobile_enabled'))

    def setUpWidgets(self, *args, **kw):
        super(SocialBase, self).setUpWidgets(*args, **kw)
        self.set_charlimit('short_text')
        if self.request.form.get('%s.twitter_ressort_enabled' % self.prefix):
            field = self.widgets['twitter_ressort'].context
            cloned = field.bind(field.context)
            cloned.required = True
            self.widgets['twitter_ressort'].context = cloned

    def applyAccountData(self, object, data):
        message_config = [
            {'type': 'facebook',
             'enabled': data.pop('facebook_main_enabled', False),
             'account': facebookAccountSource(None).MAIN_ACCOUNT},
            {'type': 'twitter',
             'enabled': data.pop('twitter_main_enabled', False),
             'account': twitterAccountSource(None).MAIN_ACCOUNT},
            {'type': 'twitter',
             'enabled': data.pop('twitter_ressort_enabled', False),
             'account': data.pop('twitter_ressort', None)}
        ]
        if data.pop('facebook_magazin_enabled', None):
            message_config.append(
                {'type': 'facebook',
                 'enabled': True,
                 'account': facebookAccountSource(None).MAGAZIN_ACCOUNT})
        if data.pop('mobile_enabled', None):
            message_config.append({
                'type': 'parse', 'enabled': True,
                # We cannot use the key ``text``, since the first positional
                # parameter of IPushNotifier.send() is also called text, which
                # would result in an TypeError.
                'override_text': data.pop('mobile_text'),
                'channels': zeit.push.interfaces.PARSE_NEWS_CHANNEL,
            })
        zeit.push.interfaces.IPushMessages(
            object).message_config = message_config


class Accounts(grok.Adapter):

    grok.context(zeit.cms.interfaces.ICMSContent)
    grok.implements(IAccounts)

    def __init__(self, context):
        super(Accounts, self).__init__(context)
        self.__parent__ = context  # make security work

    @property
    def message_config(self):
        return zeit.push.interfaces.IPushMessages(
            self.context).message_config

    @property
    def facebook_main_enabled(self):
        service = self._get_service('facebook', main=True)
        return service and service['enabled']

    @property
    def facebook_magazin_enabled(self):
        service = self._get_service('facebook', main=False)
        return service and service['account']

    @property
    def twitter_main_enabled(self):
        service = self._get_service('twitter', main=True)
        return service and service['enabled']

    @property
    def twitter_ressort(self):
        service = self._get_service('twitter', main=False)
        return service and service['account']

    @property
    def twitter_ressort_enabled(self):
        service = self._get_service('twitter', main=False)
        return service and service['enabled']

    @property
    def mobile_enabled(self):
        for service in self.message_config:
            if service['type'] != 'parse':
                continue
            if service.get(
                    'channels') == zeit.push.interfaces.PARSE_NEWS_CHANNEL:
                break
        else:
            service = None
        return service and service['enabled']

    @property
    def mobile_text(self):
        for service in self.message_config:
            if service['type'] != 'parse':
                continue
            if service.get(
                    'channels') == zeit.push.interfaces.PARSE_NEWS_CHANNEL:
                break
        else:
            service = None
        return service and service.get('text')

    def _get_service(self, type_, main=True):
        source = {
            'twitter': twitterAccountSource,
            'facebook': facebookAccountSource,
        }[type_](None)

        for service in self.message_config:
            if service['type'] != type_:
                continue
            account = service.get('account')
            is_main = (account == source.MAIN_ACCOUNT)
            if is_main == main:
                return service
        return None

    # Writing happens all services at once in the form, so we don't need to
    # worry about identifying entries in message_config (which would be doable
    # at the moment, but if we introduce individual texts or other
    # configuration, it becomes unfeasible).

    @facebook_main_enabled.setter
    def facebook_main_enabled(self, value):
        pass

    @facebook_magazin_enabled.setter
    def facebook_magazin_enabled(self, value):
        pass

    @twitter_main_enabled.setter
    def twitter_main_enabled(self, value):
        pass

    @twitter_ressort.setter
    def twitter_ressort(self, value):
        pass

    @twitter_ressort_enabled.setter
    def twitter_ressort_enabled(self, value):
        pass

    @mobile_enabled.setter
    def mobile_enabled(self, value):
        pass

    @mobile_text.setter
    def mobile_text(self, value):
        pass


class SocialAddForm(
        SocialBase, zeit.cms.content.browser.form.CommonMetadataAddForm):

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.testcontenttype.interfaces.ITestContentType).omit(
            'authors', 'xml')
    factory = zeit.cms.testcontenttype.testcontenttype.TestContentType

    field_groups = (
        zeit.cms.content.browser.form.CommonMetadataAddForm.field_groups
        + (SocialBase.social_fields,))

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
