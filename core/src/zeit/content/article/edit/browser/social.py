from zeit.cms.i18n import MessageFactory as _
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
    google = zope.schema.Bool(title=_('Enable Google Plus'))
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
            IAccounts).select('facebook', 'google')
        + zope.formlib.form.FormFields(
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
            {'type': name, 'enabled': data.get(name)}
            for name in ('facebook', 'google')]
        message_config.append(
            {'type': 'twitter',
             'enabled': data.get('twitter'),
             'account': twitterAccountSource(None).MAIN_ACCOUNT})
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
        for service in self.message_config:
            if service['type'] != 'facebook':
                continue
            return service['enabled']
        return True

    @property
    def google(self):
        for service in self.message_config:
            if service['type'] != 'google':
                continue
            return service['enabled']
        return True

    @property
    def twitter(self):
        for service in self.message_config:
            if service['type'] != 'twitter':
                continue
            if service['account'] != twitterAccountSource(None).MAIN_ACCOUNT:
                continue
            return service['enabled']
        return True

    @property
    def twitter_ressort(self):
        for service in self.message_config:
            if service['type'] != 'twitter':
                continue
            account = service.get('account')
            if account != twitterAccountSource(None).MAIN_ACCOUNT:
                return account
        return None

    # Writing happens all services at once in the form, so we don't need to
    # worry about identifying entries in message_config (which would be doable
    # at the moment, but if we introduce individual texts or other
    # configuration, it becomes unfeasible).

    @facebook.setter
    def facebook(self, value):
        pass

    @google.setter
    def google(self, value):
        pass

    @twitter.setter
    def twitter(self, value):
        pass

    @twitter_ressort.setter
    def twitter_ressort(self, value):
        pass
