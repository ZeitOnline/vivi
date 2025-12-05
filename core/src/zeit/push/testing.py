import importlib.resources
import logging
import urllib.parse

import transaction
import zope.interface

import zeit.cms.config
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


HERE = importlib.resources.files(__package__)
CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'facebook-main-account': 'fb-test',
        'facebook-breaking-news-expiration': '1800',
        'push-target-url': 'http://www.zeit.de/',
        'mobile-image-url': 'http://img.zeit.de/',
        'urbanairship-audience-group': 'subscriptions',
        'urbanairship-expire-interval': '60',
        'mobile-buttons': f'file://{HERE}/tests/fixtures/mobile-buttons.xml',
        'push-payload-templates': 'http://xml.zeit.de/data/urbanairship-templates/',
        'homepage-banner-uniqueid': 'http://xml.zeit.de/banner',
    },
    bases=(zeit.content.image.testing.CONFIG_LAYER,),
)


class ArticleConfigLayer(zeit.cms.testing.ProductConfigLayer):
    def setUp(self):
        # Break circular dependency
        import zeit.content.article.testing

        self.config = zeit.content.article.testing.CONFIG_LAYER.config
        super().setUp()


def create_fixture(repository):
    create_payload_template('', 'foo.json')
    create_payload_template('', 'eilmeldung.json')


ARTICLE_CONFIG_LAYER = ArticleConfigLayer({}, package='zeit.content.article')
ZCML_LAYER = zeit.cms.testing.ZCMLLayer((CONFIG_LAYER, ARTICLE_CONFIG_LAYER))
_zope_layer = zeit.cms.testing.RawZopeLayer(ZCML_LAYER)
ZOPE_LAYER = zeit.cms.testing.SQLIsolationSavepointLayer(_zope_layer, create_fixture)


class PushMockLayer(zeit.cms.testing.Layer):
    """Helper layer to reset mock notifiers."""

    def testSetUp(self):
        notifier = zope.component.getUtility(zeit.push.interfaces.IPushNotifier, name='homepage')
        notifier.reset()


PUSH_MOCK_LAYER = PushMockLayer()


def create_payload_template(text=None, name='template.json'):
    if not text:
        text = (
            importlib.resources.files(__package__) / 'tests/fixtures/payloadtemplate.json'
        ).read_text('utf-8')
    folder = zeit.cms.config.required('zeit.push', 'push-payload-templates')
    folder = zeit.cms.content.add.find_or_create_folder(
        *urllib.parse.urlparse(folder).path[1:].split('/')
    )
    template = zeit.content.text.jinja.JinjaTemplate()
    template.text = text
    template.title = name.split('.')[0].capitalize()
    folder[name] = template
    transaction.commit()


LAYER = zeit.cms.testing.Layer((ZOPE_LAYER, PUSH_MOCK_LAYER))


class TestCase(zeit.cms.testing.FunctionalTestCase):
    layer = LAYER


WSGI_LAYER = zeit.cms.testing.WSGILayer(LAYER)
HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(
    (
        zeit.cms.testing.WSGILayer(
            zeit.cms.testing.SQLIsolationTruncateLayer(_zope_layer, create_fixture)
        ),
        PUSH_MOCK_LAYER,
    )
)
WEBDRIVER_LAYER = zeit.cms.testing.WebdriverLayer(HTTP_LAYER)


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):
    layer = WEBDRIVER_LAYER
