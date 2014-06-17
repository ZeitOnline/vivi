from zeit.cms.i18n import MessageFactory as _
from zeit.push.facebook import facebookAccountSource
from zeit.push.twitter import twitterAccountSource
import grokcore.component as grok
import zeit.cms.browser.form
import zeit.edit.browser.form
import zope.formlib.form
import zope.interface


class Container(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Social media')


class IAccounts(zope.interface.Interface):

    facebook = zope.schema.Bool(title=_('Enable Facebook'))
    facebook_ressorts = zope.schema.Set(
        title=_('Additional Facebook'), required=False,
        value_type=zope.schema.Choice(source=facebookAccountSource))
    twitter = zope.schema.Bool(title=_('Enable Twitter'))
    twitter_ressorts = zope.schema.Set(
        title=_('Additional Twitter'), required=False,
        value_type=zope.schema.Choice(source=twitterAccountSource))


class Social(zeit.edit.browser.form.InlineForm,
             zeit.cms.browser.form.CharlimitMixin):

    legend = _('')
    prefix = 'social'
    undo_description = _('edit social media')
    form_fields = (
        zope.formlib.form.FormFields(
            zeit.push.interfaces.IPushMessages).select('long_text')
        + zope.formlib.form.FormFields(
            IAccounts).select('facebook', 'facebook_ressorts')
        +
        zope.formlib.form.FormFields(
            zeit.push.interfaces.IPushMessages).select('short_text')
        + zope.formlib.form.FormFields(
            IAccounts).select('twitter', 'twitter_ressorts')
        + zope.formlib.form.FormFields(
            zeit.push.interfaces.IPushMessages).select('enabled')
    )

    def setUpWidgets(self, *args, **kw):
        super(Social, self).setUpWidgets(*args, **kw)
        self.set_charlimit('short_text')
        self.widgets['facebook_ressorts'].extra = 'class="chosen"'
        self.widgets['twitter_ressorts'].extra = 'class="chosen"'

    def success_handler(self, action, data, errors=None):
        message_config = [
            {'type': 'facebook',
             'enabled': data.get('facebook'),
             'account': facebookAccountSource(None).MAIN_ACCOUNT},
            {'type': 'twitter',
             'enabled': data.get('twitter'),
             'account': twitterAccountSource(None).MAIN_ACCOUNT}
        ]
        for type_ in ['twitter', 'facebook']:
            for ressort in data.get('%s_ressorts' % type_, []):
                message_config.append(
                    {'type': type_,
                     'enabled': True,
                     'account': ressort})
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
        service = self._get_services('facebook', main=True)
        if not service:
            return True
        return service[0]['enabled']

    @property
    def facebook_ressorts(self):
        return set([
            x['account'] for x in self._get_services('facebook', main=False)])

    @property
    def twitter(self):
        service = self._get_services('twitter', main=True)
        if not service:
            return True
        return service[0]['enabled']

    @property
    def twitter_ressorts(self):
        return set([
            x['account'] for x in self._get_services('twitter', main=False)])

    def _get_services(self, type_, main=True):
        source = {
            'twitter': twitterAccountSource,
            'facebook': facebookAccountSource,
        }[type_](None)

        result = []
        for service in self.message_config:
            if service['type'] != type_:
                continue
            account = service.get('account')
            if not account:  # BBB
                continue
            is_main = (account == source.MAIN_ACCOUNT)
            if is_main == main:
                result.append(service)
        return result

    # Writing happens all services at once in the form, so we don't need to
    # worry about identifying entries in message_config (which would be doable
    # at the moment, but if we introduce individual texts or other
    # configuration, it becomes unfeasible).

    @facebook.setter
    def facebook(self, value):
        pass

    @facebook_ressorts.setter
    def facebook_ressort(self, value):
        pass

    @twitter.setter
    def twitter(self, value):
        pass

    @twitter_ressorts.setter
    def twitter_ressort(self, value):
        pass
