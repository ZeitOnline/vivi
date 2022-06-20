# coding: utf-8
from datetime import datetime, timedelta
from unittest import mock
from zeit.cms.content.sources import FEATURE_TOGGLES
import bugsnag
import grokcore.component as grok
import json
import logging
import pkg_resources
import pytz
import re
import requests
import sys
import urllib.parse
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.article.interfaces
import zeit.content.image.image
import zeit.content.image.interfaces
import zeit.push.interfaces
import zeit.push.message
import zope.app.appsetup.product
import zope.interface
import zope.lifecycleevent.interfaces


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
class Connection:
    """Class to send push notifications to mobile devices via urbanairship."""

    def __init__(self, base_url, application_key, master_secret,
                 legacy_url, legacy_key, legacy_secret,
                 expire_interval):
        self.base_url = base_url
        self.credentials = (application_key, master_secret)
        self.legacy_url = legacy_url
        self.legacy_credentials = (legacy_key, legacy_secret)
        self.expire_interval = expire_interval

    def send(self, text, link, **kw):
        # Since the UA payloads we need contain much more data than just text
        # and link, we talk to the IMessage object instead.
        message = kw['message']
        pushes = message.render()

        now = datetime.now(pytz.UTC)
        # See https://docs.urbanairship.com/api/ua/#schemas-pushobject
        for push in pushes:
            expiry = push.setdefault('options', {}).setdefault(
                'expiry', self.expire_interval)
            # We transmit an absolute timestamp, not relative seconds, as a
            # safetybelt against (very) delayed pushes. The format must not
            # contain microseconds, so no `isoformat`.
            expiry = now + timedelta(seconds=expiry)
            push['options']['expiry'] = expiry.strftime('%Y-%m-%dT%H:%M:%S')

        try:
            self.push(pushes)
        except Exception:
            path = urllib.parse.urlparse(link).path
            info = sys.exc_info()
            bugsnag.notify(
                info[2], traceback=info[2], context=path,
                severity='error',
                grouping_hash=message.config.get('payload_template'))
            raise

    ENDPOINT = '/push'  # for tests

    def push(self, push):
        if FEATURE_TOGGLES.find('push_airship_com'):
            self._push(push, self.legacy_url, self.legacy_credentials)
        if FEATURE_TOGGLES.find('push_airship_eu'):
            self._push(push, self.base_url, self.credentials)

    def _push(self, push, base_url, credentials):
        log.debug('Sending push to %s: %s', base_url, push)
        http = requests.Session()
        try:
            r = http.post(
                base_url + self.ENDPOINT, json=push,
                auth=credentials, headers={
                    'Accept': 'application/vnd.urbanairship+json; version=3'})
            if not r.ok:
                r.reason = '%s (%s)' % (r.reason, r.text)
            r.raise_for_status()
            return r
        except requests.exceptions.RequestException as e:
            status = getattr(e.response, 'status_code', 599)
            if status < 500:
                log.error(
                    'Semantic error during push to %s with payload %s',
                    base_url, push, exc_info=True)
                raise zeit.push.interfaces.WebServiceError(str(e))
            else:
                log.error(
                    'Technical error during push to %s with payload %s',
                    base_url, push, exc_info=True)
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
        return template(self.template_variables, output_format='json')

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
            'author_push_uuids': self.author_push_uuids
        })
        return result

    def validate_template(self, text):
        # If not proper json, a pretty good ValueError will be raised here.
        result = json.loads(text, strict=False)
        # XXX Maybe use the urbanairship python module validation API.
        return result['messages']

    def find_template(self, name):
        source = zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE
        template = source.find(name)
        if template is None:
            raise KeyError(
                'Could not find template %r in %s' % (
                    name, source.folder.uniqueId))
        return template

    @property
    def text(self):
        return self.config.get('override_text', self.context.title)

    @property
    def author_push_uuids(self):
        author_uuids = []
        for author_reference in self.context.authorships:
            if author_reference.target and \
                    author_reference.target.enable_followpush:
                uuid = zeit.cms.content.interfaces.IUUID(
                    author_reference.target)
                # Use shortened id. Friedbert adds them to UA in
                # zeit.web.site.view_author.Author.followpush_config
                author_uuids.append(uuid.shortened)
        return author_uuids

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
        parts = urllib.parse.urlparse(self.url)
        path = urllib.parse.urlunparse(
            ['', ''] + list(parts[2:])).lstrip('/')
        return '%s://%s' % (self.APP_IDENTIFIER, path)

    @property
    def log_message_details(self):
        return 'Template %s' % self.config.get('payload_template')

    def log_success(self):
        super().log_success()
        try:
            grafana = zope.component.getUtility(
                zeit.push.interfaces.IPushNotifier, name='grafana')
            grafana.send(self.text, self.url, **self.config)
        except Exception:
            log.warning(
                'Error in log_success for %s', self.url, exc_info=True)


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.push')
    return Connection(
        config['urbanairship-base-url'].rstrip('/'),
        config['urbanairship-application-key'],
        config['urbanairship-master-secret'],
        config.get('urbanairship-legacy-base-url', '').rstrip('/'),
        config.get('urbanairship-legacy-application-key'),
        config.get('urbanairship-legacy-master-secret'),
        expire_interval=int(config['urbanairship-expire-interval']))


def print_payload_documentation():
    import zeit.connector.interfaces
    import zeit.content.article.article
    import zeit.content.image.image
    import zeit.content.text.jinja

    class PayloadDocumentation(Connection):
        def push(self, data):
            print(json_dump_sphinx(data.payload))
    conn = PayloadDocumentation(
        'android_application_key', 'android_master_secret',
        'ios_application_key', 'ios_master_secret',
        'openchannel_application_key', 'openchannel_master_secret',
        'web_application_key', 'web_master_secret', expire_interval=9000)

    config = {
        'push-target-url': 'http://www.zeit.de/',
        'mobile-image-url': 'http://img.zeit.de/',
    }
    zope.app.appsetup.product.setProductConfiguration('zeit.push', config)

    article = zeit.content.article.article.Article()
    article.uniqueId = 'http://xml.zeit.de/testartikel'
    article.__name__ = 'testartikel'
    article.title = 'Titel des Testartikels'
    zope.component.provideAdapter(
        lambda x: {},
        (type(article),), zeit.connector.interfaces.IWebDAVReadProperties)
    zope.component.provideAdapter(zeit.push.message.default_push_url)
    image = zeit.content.image.image.LocalImage()
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
        'override_text': 'Some message text',
        'type': 'mobile',
        'title': 'Message title'}

    template_text = pkg_resources.resource_string(
        __name__, 'tests/fixtures/payloadtemplate.json').decode('utf-8')

    print("""\
Um ein neues Pushtemplate zu erstellen muss unter
http://vivi.zeit.de/repository/data/urbanairship-templates eine neue
Textdatei angelegt werden. In dieser Textdatei kann dann mit der `Jinja2
Template Sprache <http://jinja.pocoo.org/docs/2.9/>`_ das JSON definiert
werden, dass an Urbanairship beim veröffentlichen einer Pushnachricht
gesendet wird. Dafür muss das entsprechende Template in dem
Artikeldialog ausgewählt werden. In dem Template können sowohl auf
eine Reihe von Feldern des Artikels als auch auf die Konfiguration der
Pushnachricht zugegriffen werden::\n""")
    vars = message.template_variables
    vars['article'] = {x: '...' for x in zope.schema.getFieldNames(
        zeit.content.article.interfaces.IArticle)}
    print(json_dump_sphinx(vars))

    print("\nIm Folgenden nun ein Beispiel wie ein solches Template"
          " funktioniert. Nutzt man das Template::\n")
    print(re.sub('^', '    ', template_text, flags=re.MULTILINE))
    print("\nmit der push-Konfiguration::\n")
    print(json_dump_sphinx(message.config))
    print("\nwerden folgende Payloads an Urbanairship versandt::\n")
    template = zeit.content.text.jinja.JinjaTemplate()
    template.text = template_text
    message.find_template = lambda x: template
    conn.send('any', 'any', message=message)


def json_dump_sphinx(obj):
    return re.sub(
        '^', '    ', json.dumps(obj, indent=2, sort_keys=True),
        flags=re.MULTILINE)


@grok.subscribe(
    zeit.content.article.interfaces.IArticle,
    zope.lifecycleevent.interfaces.IObjectCreatedEvent)
def set_author_as_default_push_template(context, event):
    if not FEATURE_TOGGLES.find('push_new_articles_ua_author_tag'):
        return
    push = zeit.push.interfaces.IPushMessages(context)
    # Breaking News are also IArticle's and add messages
    # we don't want to mess it up
    if push.messages:
        return
    template_name = zope.app.appsetup.product\
        .getProductConfiguration('zeit.push')\
        .get('urbanairship-author-push-template-name')
    push.message_config = [{
        'type': 'mobile',
        'enabled': True,
        # No bw-compat needed, as it has not been enabled in production yet
        'variant': 'automatic-author',
        'payload_template': template_name}]
