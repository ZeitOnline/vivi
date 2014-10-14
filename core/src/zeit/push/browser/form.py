from zeit.cms.i18n import MessageFactory as _
from zeit.push.facebook import facebookAccountSource
from zeit.push.twitter import twitterAccountSource
import gocept.form.grouped
import grokcore.component as grok
import zeit.cms.browser.form
import zope.app.appsetup.product
import zope.formlib.form
import zope.interface
import zope.schema


class IAccounts(zope.interface.Interface):

    facebook = zope.schema.Bool(title=_('Enable Facebook'))
    facebook_magazin = zope.schema.Bool(title=_('Enable Facebook Magazin'))
    twitter = zope.schema.Bool(title=_('Enable Twitter'))
    twitter_ressort = zope.schema.Choice(
        title=_('Additional Twitter'),
        source=twitterAccountSource,
        required=False)
    mobile = zope.schema.Bool(title=_('Enable mobile push'))


class SocialBase(zeit.cms.browser.form.CharlimitMixin):

    FormFieldsFactory = zope.formlib.form.FormFields

    social_fields = gocept.form.grouped.Fields(
        _("Social media"),
        ('long_text', 'facebook', 'facebook_magazin',
         'short_text', 'twitter', 'twitter_ressort',
         'mobile', 'enabled'),
        css_class='wide-widgets column-left')

    def __init__(self, *args, **kw):
        super(SocialBase, self).__init__(*args, **kw)
        self.form_fields += (
            self.FormFieldsFactory(
                zeit.push.interfaces.IPushMessages).select('long_text')
            + self.FormFieldsFactory(
                IAccounts).select('facebook', 'facebook_magazin')
            + self.FormFieldsFactory(
                zeit.push.interfaces.IPushMessages).select('short_text')
            + self.FormFieldsFactory(
                IAccounts).select('twitter', 'twitter_ressort')
            + self.FormFieldsFactory(IAccounts).select('mobile')
            + self.FormFieldsFactory(
                zeit.push.interfaces.IPushMessages).select('enabled'))

    def setUpWidgets(self, *args, **kw):
        # Needs to be WRITEABLE_LIVE for zeit.push internals, but
        # should not be writeable through the UI while checked in.
        if not zeit.cms.checkout.interfaces.ILocalContent.providedBy(
                self.context):
            self.form_fields['enabled'].for_display = True

        super(SocialBase, self).setUpWidgets(*args, **kw)
        self.set_charlimit('short_text')

    def applyAccountData(self, data):
        message_config = [
            {'type': 'facebook',
             'enabled': data.pop('facebook', False),
             'account': facebookAccountSource(None).MAIN_ACCOUNT},
            {'type': 'twitter',
             'enabled': data.pop('twitter', False),
             'account': twitterAccountSource(None).MAIN_ACCOUNT}
        ]
        if data.pop('facebook_magazin'):
            message_config.append(
                {'type': 'facebook',
                 'enabled': True,
                 'account': facebookAccountSource(None).MAGAZIN_ACCOUNT})
        twitter_ressort = data.pop('twitter_ressort', None)
        if twitter_ressort:
            message_config.append(
                {'type': 'twitter',
                 'enabled': True,
                 'account': twitter_ressort})
        if data.pop('mobile', None):
            product_config = zope.app.appsetup.product.getProductConfiguration(
                'zeit.push')
            message_config.append({
                'type': 'parse', 'enabled': True,
                'title': product_config['parse-title-news'],
                'channels': zeit.push.interfaces.PARSE_NEWS_CHANNEL,
            })
        zeit.push.interfaces.IPushMessages(
            self.context).message_config = message_config


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
    def facebook(self):
        service = self._get_service('facebook', main=True)
        return service and service['enabled']

    @property
    def facebook_magazin(self):
        service = self._get_service('facebook', main=False)
        return service and service['account']

    @property
    def twitter(self):
        service = self._get_service('twitter', main=True)
        return service and service['enabled']

    @property
    def twitter_ressort(self):
        service = self._get_service('twitter', main=False)
        return service and service['account']

    @property
    def mobile(self):
        for service in self.message_config:
            if service['type'] != 'parse':
                continue
            if service.get(
                    'channels') == zeit.push.interfaces.PARSE_NEWS_CHANNEL:
                break
        else:
            service = None
        return service and service['enabled']

    def _get_service(self, type_, main=True):
        source = {
            'twitter': twitterAccountSource,
            'facebook': facebookAccountSource,
        }[type_](None)

        for service in self.message_config:
            if service['type'] != type_:
                continue
            account = service.get('account')
            if not account:  # BBB
                continue
            is_main = (account == source.MAIN_ACCOUNT)
            if is_main == main:
                return service
        return None

    # Writing happens all services at once in the form, so we don't need to
    # worry about identifying entries in message_config (which would be doable
    # at the moment, but if we introduce individual texts or other
    # configuration, it becomes unfeasible).

    @facebook.setter
    def facebook(self, value):
        pass

    @facebook_magazin.setter
    def facebook_magazin(self, value):
        pass

    @twitter.setter
    def twitter(self, value):
        pass

    @twitter_ressort.setter
    def twitter_ressort(self, value):
        pass

    @mobile.setter
    def mobile(self, value):
        pass


class SocialEditForm(SocialBase, zeit.cms.browser.form.EditForm):

    form_fields = zope.formlib.form.FormFields()

    @zope.formlib.form.action(
        _('Apply'), condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        self.applyAccountData(data)
        return super(SocialEditForm, self).handle_edit_action.success(data)
