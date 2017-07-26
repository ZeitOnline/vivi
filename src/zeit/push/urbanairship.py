# coding: utf-8
from __future__ import absolute_import
from datetime import datetime, timedelta
import grokcore.component as grok
import jinja2
import json
import logging
import pkg_resources
import pytz
import urbanairship
import urlparse
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.article.article
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

    @zope.cachedescriptors.property.Lazy
    def config(self):
        return zope.app.appsetup.product.getProductConfiguration(
            'zeit.push') or {}

    @property
    def expiration_datetime(self):
        return (datetime.now(pytz.UTC).replace(microsecond=0) +
                timedelta(seconds=self.expire_interval))

    def send(self, text, link, **kw):
        # XXX The API with text+link might be somewhat outdated.
        message = kw['message']
        # The expiration datetime must not contain microseconds, therefore we
        # cannot use `isoformat`.
        expiry = self.expiration_datetime.strftime('%Y-%m-%dT%H:%M:%S')
        to_push = []
        for push_message in message.render():
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


class Message(zeit.push.message.Message):

    grok.context(zeit.cms.content.interfaces.ICommonMetadata)
    grok.name('mobile')
    type = 'urbanairship'

    APP_IDENTIFIER = 'zeitapp'

    def render(self):
        template = self.load_template(self.config.get('payload_template'))
        variables = self.config.copy()
        variables['article'] = self.context
        variables['text'] = self.text
        variables['zon_link'] = self.url
        variables['app_link'] = self.app_link
        rendered_template = template.render(**variables)
        return self.validate_template(rendered_template)

    def validate_template(self, text):
        # If not proper json, a pretty good ValueError will be raised here.
        result = json.loads(text, strict=False)
        # XXX Maybe use the urbanairship python module validation API.
        return result

    def load_template(self, name):
        if isinstance(name, jinja2.Template):  # print_payload_documentation()
            return name
        source = zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE.factory
        template = source.find(name)
        if template is None:
            raise jinja2.TemplateNotFound(
                'Could not find template %s in %s' % (
                    name, source.template_folder.uniqueId))
        return jinja2.Template(template.text)

    @zope.cachedescriptors.property.Lazy
    def additional_parameters(self):
        return {'message': self}

    @zope.cachedescriptors.property.Lazy
    def text(self):
        return self.config.get('override_text', self.context.title)

    @property
    def image(self):
        images = zeit.content.image.interfaces.IImages(self.context, None)
        return getattr(images, 'image', None)

    @property
    def image_url(self):
        if self.image is None:
            return None
        cfg = zope.app.appsetup.product.getProductConfiguration('zeit.push')
        return self.image.uniqueId.replace(
            zeit.cms.interfaces.ID_NAMESPACE, cfg['mobile-image-url'])

    @property
    def app_link(self):
        parts = urlparse.urlparse(self.url)
        path = urlparse.urlunparse(['', ''] + list(parts[2:])).lstrip('/')
        return u'%s://%s' % (self.APP_IDENTIFIER, path)

    @property
    def log_message_details(self):
        return 'Template %s' % self.config.get('payload_template')


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


def print_payload_documentation():
    class PayloadDocumentation(Connection):
        def push(self, data):
            print json.dumps(data.payload, indent=2, sort_keys=True)
    conn = PayloadDocumentation(
        'android_application_key', 'android_master_secret',
        'ios_application_key', 'ios_master_secret', 'web_application_key',
        'web_master_secret', expire_interval=9000)

    config = {
        'push-target-url': 'http://www.zeit.de',
    }
    zope.app.appsetup.product.setProductConfiguration('zeit.push', config)

    article = zeit.content.article.article.Article()
    article.uniqueId = 'http://xml.zeit.de/testartikel'
    article.title = "Titel des Testartikels"
    zope.component.provideAdapter(zeit.push.message.default_push_url)

    message = Message(article)
    message.config = {
        'buttons': 'YES/NO',
        'uses_image': True,
        'image': 'http://xml.zeit.de/image',
        'image_url': 'http://img.zeit.de/image',
        'enabled': True,
        'override_text': u'Foo',
        'type': 'mobile',
        'title': u'Foo'}

    template_text = pkg_resources.resource_string(
        __name__, 'tests/fixtures/payloadtemplate.json')

    print u"""
    Um ein neues Pushtemplate zu erstellen muss unter
    http://vivi.zeit.de/repository/data/urbanairship-templates eine neue
    Textdatei angelegt werden. In dieser Textdatei kann dann mit der Jinja2
    Template Sprache (http://jinja.pocoo.org/docs/2.9/) das JSON definiert
    werden, dass an Urbanairship beim veröffentlichen einer Pushnachricht
    gesendet wird. Dafür muss das entsprechende Template in dem
    Artikeldialog ausgewählt werden. In dem Template können sowohl auf
    eine Reihe von Feldern des Artikels als auch auf die Konfiguration der
    Pushnachricht zugegriffen werden. Im Folgenden nun ein Beispiel wie ein
    solches Template funktioniert.
    Nutzt man das Template
    """
    print template_text
    print u"mit der push-Konfiguration:"
    print json.dumps(message.config, indent=2, sort_keys=True)
    print u"\nwerden folgende payloads an Urbanairship versandt:"
    message.config['payload_template'] = jinja2.Template(template_text)
    conn.send('any', 'any', message=message)
