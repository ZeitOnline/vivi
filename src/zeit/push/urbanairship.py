# coding=utf-8
from __future__ import absolute_import

from datetime import datetime, timedelta

import collections
import grokcore.component as grok
import jinja2
import json
import logging
import pytz
import urbanairship
import urllib
import urlparse
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.image.interfaces
import zeit.push.interfaces
import zeit.push.message
import zope.app.appsetup.product
import zope.cachedescriptors.property
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
        self.expire_interval = expire_interval
        self.jinja_env = jinja2.Environment(
            cache_size=0,
            loader=jinja2.FunctionLoader(load_template))

    @zope.cachedescriptors.property.Lazy
    def config(self):
        return zope.app.appsetup.product.getProductConfiguration(
            'zeit.push') or {}

    @property
    def expiration_datetime(self):
        return (datetime.now(pytz.UTC).replace(microsecond=0) +
                timedelta(seconds=self.expire_interval))

    def create_payload(self, text, link, **kw):
        push_message = kw.get('message')
        template = self.jinja_env.get_template(push_message.config.get(
            'payload_template'))
        rendered_template = template.render(**self.create_template_vars(
            text, link, push_message.context, push_message.config))
        return self.validate_template(rendered_template)

    def validate_template(self, payload_string):
        # TODO Implement it!
        # If not proper json a pretty good Value Error will be raised here
        push_messages = json.loads(payload_string, strict=False)
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
            'message': self
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
            name, zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE.factory
            .template_folder.uniqueId))
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
        'push-payload-templates': 'data/urbanairship-templates'
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
        'title': u'Foo'}
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
