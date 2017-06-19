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
        push = zeit.push.interfaces.IPushMessages(self.context)
        push.set(self.config, enabled=False)
        if not self.text:
            raise ValueError('No text configured')
        kw = {}
        kw.update(self.config)
        kw.update(self.additional_parameters)

        try:
            notifier = zope.component.getUtility(
                zeit.push.interfaces.IPushNotifier, name=self.type)
            notifier.send(self.text, self.url, **kw)
            self.log_success()
            log.info('Push notification for %s sent', self.type)
        except Exception, e:
            self.log_error(str(e))
            log.error(u'Error during push to %s with config %s',
                      self.type, self.config, exc_info=True)

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

    def log_success(self):
        self.object_log.log(_(
            'Push notification for "${name}" sent.'
            ' (Message: "${message}", Details: ${details})',
            mapping={'name': self.type.capitalize(),
                     'message': self.text,
                     'details': self.log_message_details}))

    def log_error(self, reason):
        self.object_log.log(_(
            'Error during push to ${name} ${details}: ${reason}',
            mapping={'name': self.type.capitalize(),
                     'details': self.log_message_details,
                     'reason': reason}))

    @property
    def log_message_details(self):
        return '-'


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
    def push(self):
        return zeit.push.interfaces.IPushMessages(self.context)

    @property
    def facebook_main_enabled(self):
        source = zeit.push.interfaces.facebookAccountSource(None)
        service = self.push.get(type='facebook', account=source.MAIN_ACCOUNT)
        return service and service.get('enabled')

    @facebook_main_enabled.setter
    def facebook_main_enabled(self, value):
        source = zeit.push.interfaces.facebookAccountSource(None)
        self.push.set(dict(
            type='facebook', account=source.MAIN_ACCOUNT),
            enabled=value)

    # We cannot use the key ``text``, since the first positional parameter of
    # IPushNotifier.send() is also called text, which causes TypeError.
    @property
    def facebook_main_text(self):
        source = zeit.push.interfaces.facebookAccountSource(None)
        service = self.push.get(type='facebook', account=source.MAIN_ACCOUNT)
        return service and service.get('override_text')

    @facebook_main_text.setter
    def facebook_main_text(self, value):
        source = zeit.push.interfaces.facebookAccountSource(None)
        self.push.set(dict(
            type='facebook', account=source.MAIN_ACCOUNT),
            override_text=value)

    @property
    def facebook_magazin_enabled(self):
        source = zeit.push.interfaces.facebookAccountSource(None)
        service = self.push.get(
            type='facebook', account=source.MAGAZIN_ACCOUNT)
        return service and service.get('enabled')

    @facebook_magazin_enabled.setter
    def facebook_magazin_enabled(self, value):
        source = zeit.push.interfaces.facebookAccountSource(None)
        self.push.set(dict(
            type='facebook', account=source.MAGAZIN_ACCOUNT),
            enabled=value)

    @property
    def facebook_magazin_text(self):
        source = zeit.push.interfaces.facebookAccountSource(None)
        service = self.push.get(
            type='facebook', account=source.MAGAZIN_ACCOUNT)
        return service and service.get('override_text')

    @facebook_magazin_text.setter
    def facebook_magazin_text(self, value):
        source = zeit.push.interfaces.facebookAccountSource(None)
        self.push.set(dict(
            type='facebook', account=source.MAGAZIN_ACCOUNT),
            override_text=value)

    @property
    def facebook_campus_enabled(self):
        source = zeit.push.interfaces.facebookAccountSource(None)
        service = self.push.get(type='facebook', account=source.CAMPUS_ACCOUNT)
        return service and service.get('enabled')

    @facebook_campus_enabled.setter
    def facebook_campus_enabled(self, value):
        source = zeit.push.interfaces.facebookAccountSource(None)
        self.push.set(dict(
            type='facebook', account=source.CAMPUS_ACCOUNT),
            enabled=value)

    @property
    def facebook_campus_text(self):
        source = zeit.push.interfaces.facebookAccountSource(None)
        service = self.push.get(
            type='facebook', account=source.CAMPUS_ACCOUNT)
        return service and service.get('override_text')

    @facebook_campus_text.setter
    def facebook_campus_text(self, value):
        source = zeit.push.interfaces.facebookAccountSource(None)
        self.push.set(dict(
            type='facebook', account=source.CAMPUS_ACCOUNT),
            override_text=value)

    @property
    def twitter_main_enabled(self):
        source = zeit.push.interfaces.twitterAccountSource(None)
        service = self.push.get(type='twitter', account=source.MAIN_ACCOUNT)
        return service and service.get('enabled')

    @twitter_main_enabled.setter
    def twitter_main_enabled(self, value):
        source = zeit.push.interfaces.twitterAccountSource(None)
        self.push.set(dict(
            type='twitter', account=source.MAIN_ACCOUNT),
            enabled=value)

    @property
    def twitter_ressort(self):
        return self._nonmain_twitter_service.get('account')

    @twitter_ressort.setter
    def twitter_ressort(self, value):
        self.push.set(
            dict(type='twitter', variant='ressort'), account=value)

    @property
    def twitter_ressort_enabled(self):
        return self._nonmain_twitter_service.get('enabled')

    @twitter_ressort_enabled.setter
    def twitter_ressort_enabled(self, value):
        self.push.set(
            dict(type='twitter', variant='ressort'), enabled=value)

    @property
    def _nonmain_twitter_service(self):
        source = zeit.push.interfaces.twitterAccountSource(None)
        for service in self.push.message_config:
            if service['type'] != 'twitter':
                continue
            if service.get('variant') == 'ressort':
                return service
            # BBB `variant` was introduced in zeit.push-1.21
            if service.get('account') != source.MAIN_ACCOUNT:
                return service
        return {}

    @property
    def mobile_enabled(self):
        service = self.push.get(
            type='mobile', channels=zeit.push.interfaces.CONFIG_CHANNEL_NEWS)
        return service and service.get('enabled')

    @mobile_enabled.setter
    def mobile_enabled(self, value):
        self.push.set(dict(
            type='mobile', channels=zeit.push.interfaces.CONFIG_CHANNEL_NEWS),
            enabled=value)

    @property
    def mobile_title(self):
        service = self.push.get(
            type='mobile', channels=zeit.push.interfaces.CONFIG_CHANNEL_NEWS)
        return service and service.get('title')

    @mobile_title.setter
    def mobile_title(self, value):
        self.push.set(dict(
            type='mobile', channels=zeit.push.interfaces.CONFIG_CHANNEL_NEWS),
            title=value)

    @property
    def mobile_text(self):
        service = self.push.get(
            type='mobile', channels=zeit.push.interfaces.CONFIG_CHANNEL_NEWS)
        return service and service.get('override_text')

    @mobile_text.setter
    def mobile_text(self, value):
        self.push.set(dict(
            type='mobile', channels=zeit.push.interfaces.CONFIG_CHANNEL_NEWS),
            override_text=value)

    @property
    def mobile_uses_image(self):
        service = self.push.get(
            type='mobile', channels=zeit.push.interfaces.CONFIG_CHANNEL_NEWS)
        return service and service.get('uses_image')

    @mobile_uses_image.setter
    def mobile_uses_image(self, value):
        self.push.set(dict(
            type='mobile', channels=zeit.push.interfaces.CONFIG_CHANNEL_NEWS),
            uses_image=value)

    @property
    def mobile_image(self):
        service = self.push.get(
            type='mobile', channels=zeit.push.interfaces.CONFIG_CHANNEL_NEWS)
        if not service:
            return None
        return zeit.cms.interfaces.ICMSContent(service.get('image'), None)

    @mobile_image.setter
    def mobile_image(self, value):
        if value is not None:
            value = value.uniqueId
        self.push.set(dict(
            type='mobile', channels=zeit.push.interfaces.CONFIG_CHANNEL_NEWS),
            image=value)
