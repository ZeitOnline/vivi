from zeit.cms.checkout.helper import checked_out
import plone.testing
import zeit.cms.testing
import zope.app.appsetup.product


HTTP_LAYER = zeit.cms.testing.HTTPLayer(
    zeit.cms.testing.RecordingRequestHandler,
    name='HTTPLayer', module=__name__)


WEBHOOK_LAYER = plone.testing.Layer(
    bases=(zeit.cms.testing.ZCML_LAYER, HTTP_LAYER),
    name='WebhookLayer', module=__name__)


class WebhookTest(zeit.cms.testing.ZeitCmsTestCase):

    layer = WEBHOOK_LAYER

    def test_calls_post_with_uniqueId_for_configured_urls(self):
        config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
        config['checkin-webhooks'] = (
            'http://localhost:%s' % self.layer['http_port'])
        with checked_out(self.repository['testcontent']):
            pass
        self.assertEqual(
            [{'body': '["http://xml.zeit.de/testcontent"]',
              'path': '/', 'verb': 'POST'}],
            self.layer['request_handler'].requests)
