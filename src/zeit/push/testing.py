import plone.testing
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


class MobilePushNotifier(PushNotifier):

    def get_channel_list(self, channels):
        """Required for zeit.push.mobile.Message.log_success"""
        return 'News'


BASE_ZCML_LAYER = zeit.cms.testing.ZCMLLayer('testing.zcml', product_config=(
    zeit.push.product_config +
    zeit.cms.testing.cms_product_config +
    zeit.workflow.testing.product_config +
    zeit.content.article.testing.product_config))


class PushMockLayer(plone.testing.Layer):
    """Helper layer to reset mock notifiers."""

    def testSetUp(self):
        for service in ['urbanairship', 'twitter', 'facebook', 'homepage']:
            notifier = zope.component.getUtility(
                zeit.push.interfaces.IPushNotifier, name=service)
            notifier.reset()

PUSH_MOCK_LAYER = PushMockLayer()

ZCML_LAYER = plone.testing.Layer(
    bases=(BASE_ZCML_LAYER, PUSH_MOCK_LAYER),
    name='ZCMLPushMockLayer',
    module=__name__)


class TestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZCML_LAYER


WSGI_LAYER = zeit.cms.testing.WSGILayer(
    name='WSGILayer', bases=(ZCML_LAYER,))
HTTP_LAYER = gocept.httpserverlayer.wsgi.Layer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = gocept.selenium.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))
