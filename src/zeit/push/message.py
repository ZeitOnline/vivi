import grokcore.component as grok
import zeit.cms.interfaces
import zeit.push.interfaces
import zope.component


class Message(grok.Adapter):

    grok.context(zeit.cms.interfaces.ICMSContent)
    grok.implements(zeit.push.interfaces.IMessage)
    grok.baseclass()

    get_text_from = NotImplemented

    def __init__(self, context):
        self.context = context
        self.config = {}

    def send(self):
        notifier = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name=self.type)
        if not self.text:
            raise ValueError('No text configured')
        kw = {}
        kw.update(self.config)
        kw.update(self.additional_parameters)
        notifier.send(self.text, self.url, **kw)
        self._disable_message_config()

    def _disable_message_config(self):
        push = zeit.push.interfaces.IPushMessages(self.context)
        config = push.message_config[:]
        for service in config:
            if service == self.config:
                service['enabled'] = False
        push.message_config = config

    @property
    def text(self):
        push = zeit.push.interfaces.IPushMessages(self.context)
        return getattr(push, self.get_text_from)

    @property
    def type(self):
        return self.__class__.__dict__['grokcore.component.directive.name']

    @property
    def url(self):
        return zeit.push.interfaces.IPushURL(self.context).replace(
            zeit.cms.interfaces.ID_NAMESPACE, 'http://www.zeit.de/')

    @property
    def additional_parameters(self):
        return {}


@grok.adapter(zeit.cms.interfaces.ICMSContent)
@grok.implementer(zeit.push.interfaces.IPushURL)
def default_push_url(context):
    return context.uniqueId


class AccountData(grok.Adapter):

    grok.context(zeit.cms.interfaces.ICMSContent)
    grok.implements(zeit.push.interfaces.IAccountData)

    def __init__(self, context):
        super(AccountData, self).__init__(context)
        self.__parent__ = context  # make security work

    @property
    def message_config(self):
        return zeit.push.interfaces.IPushMessages(
            self.context).message_config

    @property
    def facebook_main_enabled(self):
        source = zeit.push.interfaces.facebookAccountSource(None)
        service = self._get_facebook_service(source.MAIN_ACCOUNT)
        return service and service['enabled']

    @property
    def facebook_main_text(self):
        source = zeit.push.interfaces.facebookAccountSource(None)
        service = self._get_facebook_service(source.MAIN_ACCOUNT)
        result = service and service.get('override_text')
        if not result:  # BBB
            push = zeit.push.interfaces.IPushMessages(self.context)
            result = push.long_text
        return result

    @property
    def facebook_magazin_enabled(self):
        source = zeit.push.interfaces.facebookAccountSource(None)
        service = self._get_facebook_service(source.MAGAZIN_ACCOUNT)
        return service and service['enabled']

    @property
    def facebook_magazin_text(self):
        source = zeit.push.interfaces.facebookAccountSource(None)
        service = self._get_facebook_service(source.MAGAZIN_ACCOUNT)
        result = service and service.get('override_text')
        if not result:  # BBB
            push = zeit.push.interfaces.IPushMessages(self.context)
            result = push.long_text
        return result

    @property
    def facebook_campus_enabled(self):
        source = zeit.push.interfaces.facebookAccountSource(None)
        service = self._get_facebook_service(source.CAMPUS_ACCOUNT)
        return service and service['enabled']

    @property
    def facebook_campus_text(self):
        source = zeit.push.interfaces.facebookAccountSource(None)
        service = self._get_facebook_service(source.CAMPUS_ACCOUNT)
        result = service and service.get('override_text')
        return result

    def _get_facebook_service(self, account):
        for service in self.message_config:
            if service['type'] != 'facebook':
                continue
            if service.get('account') == account:
                return service
        return None

    @property
    def twitter_main_enabled(self):
        service = self._get_twitter_service(main=True)
        return service and service['enabled']

    @property
    def twitter_ressort(self):
        service = self._get_twitter_service(main=False)
        return service and service['account']

    @property
    def twitter_ressort_enabled(self):
        service = self._get_twitter_service(main=False)
        return service and service['enabled']

    def _get_twitter_service(self, main=True):
        source = zeit.push.interfaces.twitterAccountSource(None)
        for service in self.message_config:
            if service['type'] != 'twitter':
                continue
            account = service.get('account')
            is_main = (account == source.MAIN_ACCOUNT)
            if is_main == main:
                return service
        return None

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
        return service and service.get('override_text')

    # Writing happens all services at once in the form, so we don't need to
    # worry about identifying entries in message_config (which would be quite
    # cumbersome).

    @facebook_main_enabled.setter
    def facebook_main_enabled(self, value):
        pass

    @facebook_main_text.setter
    def facebook_main_text(self, value):
        pass

    @facebook_magazin_enabled.setter
    def facebook_magazin_enabled(self, value):
        pass

    @facebook_magazin_text.setter
    def facebook_magazin_text(self, value):
        pass

    @facebook_campus_enabled.setter
    def facebook_campus_enabled(self, value):
        pass

    @facebook_campus_text.setter
    def facebook_campus_text(self, value):
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
