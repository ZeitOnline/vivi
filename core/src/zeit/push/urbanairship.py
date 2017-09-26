# coding: utf-8
from __future__ import absolute_import
from datetime import datetime, timedelta
import bugsnag
import grokcore.component as grok
import jinja2.runtime
import json
import logging
import mock
import pkg_resources
import pytz
import sys
import urbanairship
import urlparse
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.image.interfaces
import zeit.push.interfaces
import zeit.push.message
import zope.app.appsetup.product
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

    @property
    def expiration_datetime(self):
        return (datetime.now(pytz.UTC).replace(microsecond=0) +
                timedelta(seconds=self.expire_interval))

    def send(self, text, link, **kw):
        # Since the UA payloads we need contain much more data than just text
        # and link, we talk to the IMessage object instead.
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
        try:
            for ua_push_object in to_push:
                self.push(ua_push_object)
        except:
            path = urlparse.urlparse(link).path
            info = sys.exc_info()
            bugsnag.notify(
                info[2], traceback=info[2], context=path, severity='error',
                grouping_hash=message.config.get('payload_template'))
            raise

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
        return self.validate_template(self._render())

    def _render(self):
        template = self.find_template(self.config.get('payload_template'))
        # Kludgy way to make jinja autoescape work for JSON instead of HTML.
        with mock.patch('jinja2.runtime.escape', new=json_escape):
            return template(self.template_variables, autoescape=True)

    @property
    def template_variables(self):
        result = self.config.copy()
        for key in ['enabled', 'override_text', 'type']:
            result.pop(key, None)
        result.update({
            'article': self.context,
            'text': self.text,
            'zon_link': self.url,
            'app_link': self.app_link,
            'image': self.image_url,
        })
        return result

    def validate_template(self, text):
        # If not proper json, a pretty good ValueError will be raised here.
        result = json.loads(text, strict=False)
        # XXX Maybe use the urbanairship python module validation API.
        return result['messages']

    def find_template(self, name):
        source = zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE.factory
        template = source.find(name)
        if template is None:
            raise KeyError(
                'Could not find template %r in %s' % (
                    name, source.template_folder.uniqueId))
        return template

    @property
    def text(self):
        return self.config.get('override_text', self.context.title)

    @property
    def image_url(self):
        image = self.config.get('image')
        if not image:
            return None
        cfg = zope.app.appsetup.product.getProductConfiguration('zeit.push')
        return image.replace(
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


def json_escape(value):
    if isinstance(value, basestring):
        return value.replace('"', r'\"')
    else:
        return value


def print_payload_documentation():
    import mock
    import zeit.connector.interfaces
    import zeit.content.article.article
    import zeit.content.image.image
    import zeit.content.text.jinja

    class PayloadDocumentation(Connection):
        def push(self, data):
            print json.dumps(data.payload, indent=2, sort_keys=True)
    conn = PayloadDocumentation(
        'android_application_key', 'android_master_secret',
        'ios_application_key', 'ios_master_secret', 'web_application_key',
        'web_master_secret', expire_interval=9000)

    config = {
        'push-target-url': 'http://www.zeit.de/',
        'mobile-image-url': 'http://img.zeit.de/',
    }
    zope.app.appsetup.product.setProductConfiguration('zeit.push', config)

    article = zeit.content.article.article.Article()
    article.uniqueId = 'http://xml.zeit.de/testartikel'
    article.title = 'Titel des Testartikels'
    zope.component.provideAdapter(
        lambda x: {},
        (type(article),), zeit.connector.interfaces.IWebDAVReadProperties)
    zope.component.provideAdapter(zeit.push.message.default_push_url)
    image = zeit.content.image.image.Image()
    image.uniqueId = 'http://xml.zeit.de/my-image'
    imageref = mock.Mock()
    imageref.image = image
    zope.component.provideAdapter(
        lambda x: imageref,
        (type(article),), zeit.content.image.interfaces.IImages)

    message = Message(article)
    message.config = {
        'buttons': 'YES/NO',
        'uses_image': True,
        'image': 'http://xml.zeit.de/image',
        'enabled': True,
        'override_text': u'Some message text',
        'type': 'mobile',
        'title': u'Message title'}

    template_text = pkg_resources.resource_string(
        __name__, 'tests/fixtures/payloadtemplate.json')

    print """\
Um ein neues Pushtemplate zu erstellen muss unter
http://vivi.zeit.de/repository/data/urbanairship-templates eine neue
Textdatei angelegt werden. In dieser Textdatei kann dann mit der Jinja2
Template Sprache (http://jinja.pocoo.org/docs/2.9/) das JSON definiert
werden, dass an Urbanairship beim veröffentlichen einer Pushnachricht
gesendet wird. Dafür muss das entsprechende Template in dem
Artikeldialog ausgewählt werden. In dem Template können sowohl auf
eine Reihe von Feldern des Artikels als auch auf die Konfiguration der
Pushnachricht zugegriffen werden:"""
    vars = message.template_variables
    vars['article'] = {x: '...' for x in zope.schema.getFieldNames(
        zeit.content.article.interfaces.IArticle)}
    print json.dumps(vars, indent=2, sort_keys=True)

    print ("\nIm Folgenden nun ein Beispiel wie ein solches Template"
           " funktioniert. Nutzt man das Template")
    print template_text
    print "\nmit der push-Konfiguration"
    print json.dumps(message.config, indent=2, sort_keys=True)
    print "\nwerden folgende Payloads an Urbanairship versandt:"
    template = zeit.content.text.jinja.JinjaTemplate()
    template.text = template_text
    message.find_template = lambda x: template
    conn.send('any', 'any', message=message)
