import gocept.selenium
import logging
import zeit.cms.testing
import zeit.content.article.testing
import zeit.push.interfaces
import zeit.workflow.testing
import zope.interface


log = logging.getLogger(__name__)


class PushNotifier(object):

    zope.interface.implements(zeit.push.interfaces.IPushNotifier)

    def __init__(self):
        self.reset()

    def reset(self):
        self.calls = []

    def send(self, text, link, **kw):
        self.calls.append((text, link, kw))
        log.info('PushNotifier.send(%s)', dict(
            text=text, link=link, kw=kw))


ZCML_LAYER = zeit.cms.testing.ZCMLLayer('testing.zcml', product_config=(
    zeit.push.product_config
    + zeit.cms.testing.cms_product_config
    + zeit.workflow.testing.product_config
    + zeit.content.article.testing.product_config))


class TestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZCML_LAYER

    def setUp(self):
        super(TestCase, self).setUp()
        for service in ['parse', 'urbanairship', 'twitter', 'facebook',
                        'homepage', 'ios-legacy', 'wrapper']:
            notifier = zope.component.getUtility(
                zeit.push.interfaces.IPushNotifier, name=service)
            notifier.reset()


WSGI_LAYER = zeit.cms.testing.WSGILayer(
    name='WSGILayer', bases=(ZCML_LAYER,))
HTTP_LAYER = gocept.httpserverlayer.wsgi.Layer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = gocept.selenium.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))
