import importlib.resources
import logging
import urllib.parse

import gocept.selenium
import hvac
import plone.testing
import zope.interface

import zeit.cms.testing
import zeit.content.image.testing
import zeit.content.text.jinja
import zeit.push.interfaces


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
class PushNotifier:
    def __init__(self):
        self.reset()

    def reset(self):
        self.calls = []

    def send(self, text, link, **kw):
        self.calls.append((text, link, kw))
        log.info('PushNotifier.send(%s)', {'text': text, 'link': link, 'kw': kw})


product_config = """\
<product-config zeit.push>
  twitter-accounts file://{fixtures}/twitter-accounts.xml
  twitter-main-account twitter-test
  twitter-print-account twitter-print
  facebook-accounts file://{fixtures}/facebook-accounts.xml
  facebook-main-account fb-test
  facebook-magazin-account fb-magazin
  facebook-campus-account fb-campus
  facebook-zett-account fb-zett
  facebook-breaking-news-expiration 1800
  push-target-url http://www.zeit.de/
  mobile-image-url http://img.zeit.de/
  urbanairship-audience-group subscriptions
  urbanairship-author-push-template-name authors.json
  mobile-buttons file://{fixtures}/mobile-buttons.xml
  push-payload-templates http://xml.zeit.de/data/urbanairship-templates/
  homepage-banner-uniqueid http://xml.zeit.de/banner
</product-config>
""".format(fixtures='%s/tests/fixtures' % importlib.resources.files(__package__))


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    product_config, bases=(zeit.content.image.testing.CONFIG_LAYER,)
)


class ArticleConfigLayer(zeit.cms.testing.ProductConfigLayer):
    def setUp(self):
        # Break circular dependency
        import zeit.content.article.testing

        config = zeit.content.article.testing.product_config
        self.config = self.loadConfiguration(config, self.package)
        super().setUp()


ARTICLE_CONFIG_LAYER = ArticleConfigLayer({}, package='zeit.content.article')
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER, ARTICLE_CONFIG_LAYER))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))


class PushMockLayer(plone.testing.Layer):
    """Helper layer to reset mock notifiers."""

    def testSetUp(self):
        for service in ['urbanairship', 'twitter', 'facebook', 'homepage']:
            notifier = zope.component.getUtility(zeit.push.interfaces.IPushNotifier, name=service)
            notifier.reset()


PUSH_MOCK_LAYER = PushMockLayer()


@zope.interface.implementer(zeit.push.interfaces.ITwitterCredentials)
class TwitterCredentials:
    vault = hvac.Client()
    secret = 'zon/v1/twitter/vivi-zeitpush-tests'

    def _read(self):
        return self.vault.secrets.kv.v1.read_secret(self.secret, mount_point='')['data']

    def access_token(self, account_name):
        return self._read()['access_token']

    def refresh_token(self, account_name):
        return self._read()['refresh_token']

    def update(self, account_name, access_token, refresh_token):
        assert account_name == 'twitter-test'
        secret = self._read()
        secret['access_token'] = access_token
        secret['refresh_token'] = refresh_token
        self.vault.secrets.kv.v1.create_or_update_secret(self.secret, secret, mount_point='')


class UrbanairshipTemplateLayer(plone.testing.Layer):
    defaultBases = (ZOPE_LAYER,)

    def create_template(self, text=None, name='template.json'):
        if not text:
            text = (
                importlib.resources.files(__package__) / 'tests/fixtures/payloadtemplate.json'
            ).read_text('utf-8')
        with zeit.cms.testing.site(self['zodbApp']):
            with zeit.cms.testing.interaction():
                cfg = zope.app.appsetup.product.getProductConfiguration('zeit.push')
                folder = zeit.cms.content.add.find_or_create_folder(
                    *urllib.parse.urlparse(cfg['push-payload-templates']).path[1:].split('/')
                )
                template = zeit.content.text.jinja.JinjaTemplate()
                template.text = text
                template.title = name.split('.')[0].capitalize()
                folder[name] = template

    def setUp(self):
        self['create_template'] = self.create_template

    def testSetUp(self):
        self.create_template('', 'foo.json')
        self.create_template('', 'eilmeldung.json')
        self.create_template(
            (importlib.resources.files(__package__) / 'tests/fixtures/authors.json').read_text(
                'utf-8'
            ),
            'authors.json',
        )


URBANAIRSHIP_TEMPLATE_LAYER = UrbanairshipTemplateLayer()

LAYER = plone.testing.Layer(name='Layer', bases=(URBANAIRSHIP_TEMPLATE_LAYER, PUSH_MOCK_LAYER))


class TestCase(zeit.cms.testing.FunctionalTestCase):
    layer = LAYER

    def create_payload_template(self, text=None, name='template.json'):
        self.layer['create_template'](text, name)


WSGI_LAYER = zeit.cms.testing.WSGILayer(name='WSGILayer', bases=(LAYER,))
HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = zeit.cms.testing.WebdriverLayer(name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,)
)


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):
    layer = WEBDRIVER_LAYER
