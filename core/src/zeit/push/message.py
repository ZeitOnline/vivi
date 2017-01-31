from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import logging
import zeit.cms.interfaces
import zeit.objectlog.interfaces
import zeit.push.interfaces
import zope.cachedescriptors.property
import zope.component


log = logging.getLogger(__name__)


class Message(grok.Adapter):

    grok.context(zeit.cms.interfaces.ICMSContent)
    grok.implements(zeit.push.interfaces.IMessage)
    grok.baseclass()

    get_text_from = NotImplemented

    def __init__(self, context):
        self.context = context
        self.config = {}

    def send(self):
        """Send push notification to external service.

        We *never* want to re-send a push notification on publish, even if the
        initial notification failed, since the information could be outdated.
        Therefore we must disable the notification before anything else.
        Re-sending can be done manually by re-enabling the service.

        """
        self._disable_message_config()
        if not self.text:
            raise ValueError('No text configured')
        kw = {}
        kw.update(self.config)
        kw.update(self.additional_parameters)
        self.send_push_notification(self.type, **kw)

    def send_push_notification(self, service_name, **kw):
        """Forward sending of the acutal push notification to `IPushNotifier`.

        Log success and error in the object log, so the user knows about a
        failure and can act on it.

        """
        try:
            notifier = zope.component.getUtility(
                zeit.push.interfaces.IPushNotifier, name=service_name)
            notifier.send(self.text, self.url, **kw)
            self.log_success(name=service_name)
            log.info('Push notification for %s sent', service_name)
        except Exception, e:
            self.log_error(name=service_name, reason=str(e))
            log.error(u'Error during push to %s with config %s',
                      service_name, self.config, exc_info=True)

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
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.push')
        return zeit.push.interfaces.IPushURL(self.context).replace(
            zeit.cms.interfaces.ID_NAMESPACE, config['push-target-url'])

    @property
    def additional_parameters(self):
        return {}

    @zope.cachedescriptors.property.Lazy
    def object_log(self):
        return zeit.objectlog.interfaces.ILog(self.context)

    def log_success(self, name):
        self.object_log.log(_(
            'Push notification for "${name}" sent. (Message: "${message}")',
            mapping={'name': name.capitalize(), 'message': self.text}))

    def log_error(self, name, reason):
        self.object_log.log(_(
            'Error during push to ${name}: ${reason}',
            mapping={'name': name.capitalize(), 'reason': reason}))


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
            if service['type'] != 'mobile':
                continue
            if service.get(
                    'channels') == zeit.push.interfaces.CONFIG_CHANNEL_NEWS:
                break
        else:
            service = None
        return service and service['enabled']

    @property
    def mobile_text(self):
        for service in self.message_config:
            if service['type'] != 'mobile':
                continue
            if service.get(
                    'channels') == zeit.push.interfaces.CONFIG_CHANNEL_NEWS:
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
