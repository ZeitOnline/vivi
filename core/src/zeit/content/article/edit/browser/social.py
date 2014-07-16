from zeit.cms.i18n import MessageFactory as _
from zeit.push.twitter import twitterAccountSource
from zeit.push.facebook import facebookAccountSource
import grokcore.component as grok
import zeit.cms.browser.form
import zeit.edit.browser.form
import zope.formlib.form
import zope.interface


class Container(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Social media')


class IAccounts(zope.interface.Interface):

    facebook = zope.schema.Bool(title=_('Enable Facebook'))
    facebook_magazin = zope.schema.Bool(title=_('Enable Facebook Magazin'))
    twitter = zope.schema.Bool(title=_('Enable Twitter'))
    twitter_ressort = zope.schema.Choice(
        title=_('Additional Twitter'),
        source=twitterAccountSource,
        required=False)


class Social(zeit.edit.browser.form.InlineForm,
             zeit.cms.browser.form.CharlimitMixin):

    legend = _('')
    prefix = 'social'
    undo_description = _('edit social media')
    form_fields = (
        zope.formlib.form.FormFields(
            zeit.push.interfaces.IPushMessages).select('long_text')
        + zope.formlib.form.FormFields(
            IAccounts).select('facebook', 'facebook_magazin')
        +
        zope.formlib.form.FormFields(
            zeit.push.interfaces.IPushMessages).select('short_text')
        + zope.formlib.form.FormFields(
            IAccounts).select('twitter', 'twitter_ressort')
        + zope.formlib.form.FormFields(
            zeit.push.interfaces.IPushMessages).select('enabled')
    )

    def setUpWidgets(self, *args, **kw):
        super(Social, self).setUpWidgets(*args, **kw)
        self.set_charlimit('short_text')

    def success_handler(self, action, data, errors=None):
        message_config = [
            {'type': 'facebook',
             'enabled': data.get('facebook'),
             'account': facebookAccountSource(None).MAIN_ACCOUNT},
            {'type': 'twitter',
             'enabled': data.get('twitter'),
             'account': twitterAccountSource(None).MAIN_ACCOUNT}
        ]
        if data.get('facebook_magazin'):
            message_config.append(
                {'type': 'facebook',
                 'enabled': True,
                 'account': facebookAccountSource(None).MAGAZIN_ACCOUNT})
        twitter_ressort = data.get('twitter_ressort')
        if twitter_ressort:
            message_config.append(
                {'type': 'twitter',
                 'enabled': True,
                 'account': twitter_ressort})
        zeit.push.interfaces.IPushMessages(
            self.context).message_config = message_config
        return super(Social, self).success_handler(action, data, errors)


class Accounts(grok.Adapter):

    grok.context(zeit.cms.interfaces.ICMSContent)
    grok.implements(IAccounts)

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
