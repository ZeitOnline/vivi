# coding=utf-8
from __future__ import absolute_import

from datetime import datetime, timedelta

from zeit.push.interfaces import CONFIG_CHANNEL_NEWS, CONFIG_CHANNEL_BREAKING
import collections
import grokcore.component as grok
import jinja2
import json
import logging
import pytz
import urbanairship
import urllib
import urlparse
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.image.interfaces
import zeit.push.interfaces
import zeit.push.message
import zope.app.appsetup.product
import zope.cachedescriptors.property
import zope.component
import zope.i18n
import zope.interface


log = logging.getLogger(__name__)


class Connection(object):
    """Class to send push notifications to mobile devices via urbanairship."""

    zope.interface.implements(zeit.push.interfaces.IPushNotifier)

    LANGUAGE = 'de'
    APP_IDENTIFIER = 'zeitapp'

    def __init__(self, android_application_key, android_master_secret,
                 ios_application_key, ios_master_secret,
                 web_application_key, web_master_secret, expire_interval,
                 ):
        self.credentials = {
            'android': [android_application_key, android_master_secret],
            'ios': [ios_application_key, ios_master_secret],
            'web': [web_application_key, web_master_secret]
        }
        # TODO Clean this up. I dont know yet which parts rely on this
        # interface
        self.android_application_key = android_application_key
        self.android_master_secret = android_master_secret
        self.ios_application_key = ios_application_key
        self.ios_master_secret = ios_master_secret
        self.web_application_key = web_application_key
        self.web_master_secret = web_master_secret
        self.expire_interval = expire_interval
        self.jinja_env = jinja2.Environment(
            cache_size=0,
            loader=jinja2.FunctionLoader(load_template))

    @zope.cachedescriptors.property.Lazy
    def config(self):
        return zope.app.appsetup.product.getProductConfiguration(
            'zeit.push') or {}

    # TODO Headlines have to be implemented in another way
    # def get_headline(self, channels):
    #     """Return translation for the headline, which depends on the channel.
    #
    #     Since the channel is used to classify the push notification as
    #     ordinary news or breaking news, it also influences the headline.
    #
    #     """
    #     if self.config.get(CONFIG_CHANNEL_NEWS) in channels:
    #         headline = _('push-news-title')
    #     else:
    #         headline = _('push-breaking-title')
    #
    #     # There's no i18n in the mobile app, so we translate to a hard-coded
    #     # language here.
    #     return zope.i18n.translate(headline, target_language=self.LANGUAGE)

    @property
    def expiration_datetime(self):
        return (datetime.now(pytz.UTC).replace(microsecond=0) +
                timedelta(seconds=self.expire_interval))

    def create_payload(self, text, link, **kw):
        article = kw.get('context')
        push_message = kw.get('push_config')
        template = self.jinja_env.get_template(push_message.get(
            'payload_template'))
        rendered_template = template.render(**self.create_template_vars(
            text, link, article, push_message))
        return self.validate_template(rendered_template)
        # TODO Use standard headline

    def validate_template(self, payload_string):
        # TODO Implement it!
        # If not proper json a pretty good Value Error will be raised here
        push_messages = json.loads(payload_string)
        # Work with colander here?
        # Maybe make use of functionality of the urbanairship python module,
        #  or its validation API
        return push_messages

    def send(self, text, link, **kw):
        # The expiration datetime must not contain microseconds, therefore we
        # cannot use `isoformat`.
        expiry = self.expiration_datetime.strftime('%Y-%m-%dT%H:%M:%S')
        to_push = []
        push_messages = self.create_payload(text, link, **kw)
        for push_message in push_messages:
            # Check out
            # https://docs.urbanairship.com/api/ua/#push-object
            for device in push_message.get('device_types', []):
                application_credentials = self.credentials.get(device,
                                                               [None, None])
                ua_push_object = urbanairship.Airship(
                    *application_credentials
                ).create_push()
                ua_push_object.expiry = expiry
                ua_push_object.audience = push_message['audience']
                ua_push_object.device_types = urbanairship.device_types(device)
                ua_push_object.notification = push_message['notification']
                to_push.append(ua_push_object)

        # Urban airship does support batch pushing, but
        # the python module does not
        # https://github.com/urbanairship/python-library/issues/34
        # Still we should not push each object directly after is
        # created, because otherwise the whole push process can fail with
        # a later object
        # Great validation would be a solution to this problem :)
        for ua_push_object in to_push:
            self.push(ua_push_object)

    def push(self, push):
        log.debug('Sending Push to Urban Airship: %s', push.payload)
        try:
            push.send()
        except urbanairship.common.Unauthorized:
            log.error(
                'Semantic error during push to Urban Airship with payload %s',
                push.payload, exc_info=True)
            raise zeit.push.interfaces.WebServiceError('Unauthorized')
        except urbanairship.common.AirshipFailure, e:
            log.error(
                'Technical error during push to Urban Airship with payload %s',
                push.payload, exc_info=True)
            raise zeit.push.interfaces.TechnicalError(str(e))

    # XXX Not used but maybe we will use something simmilar in another form
    @staticmethod
    def add_tracking(url, channels, device):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.push') or {}
        if config.get(CONFIG_CHANNEL_BREAKING) in channels:
            channel = 'eilmeldung'
        else:
            channel = 'wichtige_news'
        if device == 'android':
            device = 'andpush'
        else:
            device = 'iospush'

        tracking = collections.OrderedDict(sorted(
            {
                'wt_zmc': 'fix.int.zonaudev.push.{channel}.zeitde.{'
                          'device}.link.x'.format(channel=channel,
                                                  device=device),
                'utm_medium': 'fix',
                'utm_source': 'push_zonaudev_int',
                'utm_campaign': channel,
                'utm_content': 'zeitde_{device}_link_x'.format(device=device),
            }.items())
        )
        parts = list(urlparse.urlparse(url))
        query = collections.OrderedDict(urlparse.parse_qs(parts[4]))
        for key, value in tracking.items():
            query[key] = value
        parts[4] = urllib.urlencode(query, doseq=True)
        return urlparse.urlunparse(parts)

    def create_template_vars(self, text, link, article, push_config):
        parts = urlparse.urlparse(link)
        path = urlparse.urlunparse(['', ''] + list(parts[2:])).lstrip('/')
        full_link = u'%s://%s/%s' % (parts.scheme, parts.netloc, path)
        deep_link = u'%s://%s' % (self.APP_IDENTIFIER, path)
        vars = push_config
        vars['article'] = article
        vars['text'] = text
        vars['zon_link'] = full_link
        vars['app_link'] = deep_link
        return vars


class Message(zeit.push.message.Message):

    grok.context(zeit.cms.content.interfaces.ICommonMetadata)
    grok.name('mobile')
    type = 'urbanairship'

    @property
    def log_message_details(self):
        template = self.config.get('payload_template')
        return 'Pushed with template %s' % template

    @zope.cachedescriptors.property.Lazy
    def text(self):
        return self.config.get('override_text', self.context.title)

    @zope.cachedescriptors.property.Lazy
    def additional_parameters(self):
        result = {
            'mobile_title': self.config.get('title'),
            'context': self.context,
            'push_config': self.config
        }
        if self.image:
            result['image_url'] = self.image.uniqueId.replace(
                zeit.cms.interfaces.ID_NAMESPACE,
                self.product_config['mobile-image-url'])
        return result

    @property
    def image(self):
        images = zeit.content.image.interfaces.IImages(self.context, None)
        return getattr(images, 'image', None)

    @zope.cachedescriptors.property.Lazy
    def product_config(self):
        return zope.app.appsetup.product.getProductConfiguration('zeit.push')


@grok.subscribe(
    zeit.cms.content.interfaces.ICommonMetadata,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def set_push_news_flag(context, event):
    push = zeit.push.interfaces.IPushMessages(context)
    for service in push.message_config:
        # Just ignore channels for now
        # Everything which is would get this flag now
        # Is this relvant for anything else then the CP described in VIV-526?
        if (service['type'] == 'mobile' and
                service.get('enabled')):
            context.push_news = True
            break


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.push')
    return Connection(
        android_application_key=config['urbanairship-android-application-key'],
        android_master_secret=config['urbanairship-android-master-secret'],
        ios_application_key=config['urbanairship-ios-application-key'],
        ios_master_secret=config['urbanairship-ios-master-secret'],
        web_application_key=config['urbanairship-web-application-key'],
        web_master_secret=config['urbanairship-web-master-secret'],
        expire_interval=int(config['urbanairship-expire-interval']))


def load_template(name):
    """
    Returns the template text as unicode
    :param name: Name
    :return: unicode
    """
    template = zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE.factory.find(name)
    if not template:
        raise jinja2.TemplateNotFound("Could not find template %s in %s" % (
            name, zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE))
    return template.text


def print_payload_documentation():
    import zeit.content.article.article
    import pkg_resources

    class PayloadDocumentation(Connection):

        def push(self, data):
            print json.dumps(data.payload, indent=2, sort_keys=True)

    def build_test_arcicle(article_url):
        article = zeit.content.article.article.Article()
        article.uniqueId = article_url
        article.title = "Titel des Testartikels"
        return article

    config = {
        'push-target-url': 'http://www.zeit.de',
        'push-payload-templates': 'data/payload-templates'
    }
    zope.app.appsetup.product.setProductConfiguration('zeit.push', config)
    conn = PayloadDocumentation(
        'android_application_key', 'android_master_secret',
        'ios_application_key', 'ios_master_secret', 'web_application_key',
        'web_master_secret', expire_interval=9000)
    article_url = 'http://www.zeit.de/testartikel'
    article = build_test_arcicle(article_url)
    # Use a different jinja environment here which uses the test payload
    # template
    payload_path = "{fixtures}/payloadtemplate.json".format(
        fixtures=pkg_resources.resource_filename(
            __name__, 'tests/fixtures'))
    template_text = None
    with open(payload_path) as f:
        template_text = f.read().decode('utf-8')
    conn.jinja_env = jinja2.Environment(
        loader=jinja2.FunctionLoader(lambda x: template_text))
    push_config = {
        'buttons': 'YES/NO',
        'uses_image': True,
        'image': 'IMAGE_URL',
        'enabled': True,
        'override_text': u'Foo',
        'type': 'mobile',
        'title': u'Bar'}
    params = {
        'push_config': push_config,
        'context': article,
    }
    template_vars = conn.create_template_vars('PushTitle',
                                              article_url,
                                              article,
                                              push_config)
    print u"""
    Um ein neues Pushtemplate zu erstellen muss unter
    http://vivi.zeit.de/repository/{template_path} eine neue Textdatei
    angelegt werden. In dieser Textdatei kann dann mithilfe der Jinja2
    Template Sprache (http://jinja.pocoo.org/docs/2.9/) das JSON definiert
    werden, dass an Urbanairship beim veröffentlichen einer Pushnachricht
    gesendet wird. Dafür muss das entsprechende Template in dem
    Artikeldialog ausgewählt werden. In dem Template können sowohl auf
    eine Reihe von Feldern des Artikels als auch auf die Konfiguration der
    Pushnachricht zugegriffen werden. Im Folgenden nun ein Beispiel wie ein
    solches Template funktioniert.
    Nutz man das Template
    {template_text}
    """.format(
        template_path=config.get('push-payload-templates'),
        template_text=template_text
        )
    print u"mit der push-Konfiguration:"
    template_vars['article'] = 'article'
    print json.dumps(template_vars, indent=2, sort_keys=True)
    print u"werden folgende payloads an Urbanairship versandt:"
    conn.send('PushTitle', article_url, **params)
