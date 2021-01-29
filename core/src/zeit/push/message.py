from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import logging
import urllib.parse
import zeit.cms.interfaces
import zeit.objectlog.interfaces
import zeit.push.interfaces
import zope.cachedescriptors.property
import zope.component


log = logging.getLogger(__name__)


@grok.implementer(zeit.push.interfaces.IMessage)
class Message(grok.Adapter):

    grok.context(zeit.cms.interfaces.ICMSContent)
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
        kw['message'] = self

        try:
            notifier = zope.component.getUtility(
                zeit.push.interfaces.IPushNotifier, name=self.type)
            notifier.send(self.text, self.url, **kw)
            self.log_success()
            log.info('Push notification for %s sent', self.type)
        except Exception as e:
            self.log_error(str(e))
            log.error(u'Error during push to %s with config %s',
                      self.type, self.config, exc_info=True)

    def _disable_message_config(self):
        push = zeit.push.interfaces.IPushMessages(self.context)
        push.set(self.config, enabled=False)

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

    @staticmethod
    def add_query_params(url, **params):
        parts = list(urllib.parse.urlparse(url))
        query = dict(urllib.parse.parse_qs(parts[4]))
        query.update(params)
        parts[4] = urllib.parse.urlencode(query)
        return urllib.parse.urlunparse(parts)

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


@grok.implementer(zeit.push.interfaces.IAccountData)
class AccountData(grok.Adapter):

    grok.context(zeit.cms.interfaces.ICMSContent)

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
    def facebook_zett_enabled(self):
        source = zeit.push.interfaces.facebookAccountSource(None)
        service = self.push.get(type='facebook', account=source.ZETT_ACCOUNT)
        return service and service.get('enabled')

    @facebook_zett_enabled.setter
    def facebook_zett_enabled(self, value):
        source = zeit.push.interfaces.facebookAccountSource(None)
        self.push.set(dict(
            type='facebook', account=source.ZETT_ACCOUNT),
            enabled=value)

    @property
    def facebook_zett_text(self):
        source = zeit.push.interfaces.facebookAccountSource(None)
        service = self.push.get(
            type='facebook', account=source.ZETT_ACCOUNT)
        return service and service.get('override_text')

    @facebook_zett_text.setter
    def facebook_zett_text(self, value):
        source = zeit.push.interfaces.facebookAccountSource(None)
        self.push.set(dict(
            type='facebook', account=source.ZETT_ACCOUNT),
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
    def twitter_ressort_text(self):
        return self._nonmain_twitter_service.get('override_text')

    @twitter_ressort_text.setter
    def twitter_ressort_text(self, value):
        self.push.set(
            dict(type='twitter', variant='ressort'), override_text=value)

    @property
    def twitter_ressort(self):
        return self._nonmain_twitter_service.get('account')

    @twitter_ressort.setter
    def twitter_ressort(self, value):
        service = self._nonmain_twitter_service
        enabled = None
        # BBB `variant` was introduced in zeit.push-1.21
        if service and 'variant' not in service:
            self.push.delete(service)
            enabled = service.get('enabled')
        self.push.set(
            dict(type='twitter', variant='ressort'), account=value)
        if enabled is not None:
            self.twitter_ressort_enabled = enabled

    @property
    def twitter_ressort_enabled(self):
        return self._nonmain_twitter_service.get('enabled')

    @twitter_ressort_enabled.setter
    def twitter_ressort_enabled(self, value):
        service = self._nonmain_twitter_service
        account = None
        # BBB `variant` was introduced in zeit.push-1.21
        if service and 'variant' not in service:
            self.push.delete(service)
            account = service.get('account')
        self.push.set(
            dict(type='twitter', variant='ressort'), enabled=value)
        if account is not None:
            self.twitter_ressort = account

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
    def twitter_print_enabled(self):
        source = zeit.push.interfaces.twitterAccountSource(None)
        service = self.push.get(type='twitter', account=source.PRINT_ACCOUNT)
        return service and service.get('enabled')

    @twitter_print_enabled.setter
    def twitter_print_enabled(self, value):
        source = zeit.push.interfaces.twitterAccountSource(None)
        self.push.set(dict(
            type='twitter', account=source.PRINT_ACCOUNT),
            enabled=value)

    @property
    def twitter_print_text(self):
        source = zeit.push.interfaces.twitterAccountSource(None)
        service = self.push.get(type='twitter', account=source.PRINT_ACCOUNT)
        return service and service.get('override_text')

    @twitter_print_text.setter
    def twitter_print_text(self, value):
        source = zeit.push.interfaces.twitterAccountSource(None)
        self.push.set(
            dict(type='twitter', account=source.PRINT_ACCOUNT),
            override_text=value)

    @property
    def mobile_enabled(self):
        service = self._mobile_service
        return service and service.get('enabled')

    @mobile_enabled.setter
    def mobile_enabled(self, value):
        self._set_mobile_service(enabled=value)

    @property
    def mobile_title(self):
        service = self._mobile_service
        return service and service.get('title')

    @mobile_title.setter
    def mobile_title(self, value):
        self._set_mobile_service(title=value)

    @property
    def mobile_text(self):
        service = self._mobile_service
        return service and service.get('override_text')

    @mobile_text.setter
    def mobile_text(self, value):
        self._set_mobile_service(override_text=value)

    @property
    def mobile_uses_image(self):
        service = self._mobile_service
        return service and service.get('uses_image')

    @mobile_uses_image.setter
    def mobile_uses_image(self, value):
        self._set_mobile_service(uses_image=value)

    @property
    def mobile_image(self):
        service = self._mobile_service
        if not service:
            return None
        return zeit.cms.interfaces.ICMSContent(service.get('image'), None)

    @mobile_image.setter
    def mobile_image(self, value):
        if value is not None:
            value = value.uniqueId
        self._set_mobile_service(image=value)

    @property
    def mobile_buttons(self):
        service = self._mobile_service
        return service and service.get('buttons')

    @mobile_buttons.setter
    def mobile_buttons(self, value):
        self._set_mobile_service(buttons=value)

    @property
    def mobile_payload_template(self):
        service = self._mobile_service
        return service and zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE\
            .factory.find(service.get('payload_template'))

    @mobile_payload_template.setter
    def mobile_payload_template(self, value):
        if value is None:
            token = None
        else:
            token = zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE\
                .factory.getToken(value)
        self._set_mobile_service(payload_template=token)

    @property
    def _mobile_service(self):
        service = self.push.get(type='mobile', variant='manual')
        if service:
            return service
        # BBB `variant` was introduced in zeit.push-1.26.0
        service = self.push.get(type='mobile')
        if service and not service.get('variant'):
            return service

    def _set_mobile_service(self, **kw):
        service = self._mobile_service
        # BBB `variant` was introduced in zeit.push-1.26.0
        if service and not service.get('variant'):
            self.push.delete(service)
            for key, value in service.items():
                if key not in kw:
                    kw[key] = value
        self.push.set(dict(type='mobile', variant='manual'), **kw)
