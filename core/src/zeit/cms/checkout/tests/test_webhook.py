from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.sources import Product
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import lxml.objectify
import mock
import plone.testing
import zeit.cms.checkout.webhook
import zeit.cms.testing


HTTP_LAYER = zeit.cms.testing.HTTPLayer(
    zeit.cms.testing.RecordingRequestHandler,
    name='HTTPLayer', module=__name__)


WEBHOOK_LAYER = plone.testing.Layer(
    bases=(zeit.cms.testing.ZCML_LAYER, HTTP_LAYER),
    name='WebhookLayer', module=__name__)


class WebhookTest(zeit.cms.testing.ZeitCmsTestCase):

    layer = WEBHOOK_LAYER

    def setUp(self):
        super(WebhookTest, self).setUp()
        self.config = (
            '<webhooks><webhook url="http://localhost:%s"/></webhooks>' %
            self.layer['http_port'])
        self.patch = mock.patch(
            'zeit.cms.checkout.webhook.HookSource._get_tree',
            new=lambda x: lxml.objectify.fromstring(self.config))
        self.patch.start()
        source = zeit.cms.checkout.webhook.HOOKS.factory
        # XXX Have to pass the instance because of zc.factory init shenanigans.
        source.getValues.invalidate(source)

    def tearDown(self):
        self.patch.stop()
        super(WebhookTest, self).tearDown()

    def test_calls_post_with_uniqueId_for_configured_urls(self):
        with checked_out(self.repository['testcontent']):
            pass
        self.assertEqual(
            [{'body': '["http://xml.zeit.de/testcontent"]',
              'path': '/', 'verb': 'POST'}],
            self.layer['request_handler'].requests)

    def test_calls_hook_when_adding_new_object_to_repository(self):
        self.repository['testcontent2'] = ExampleContentType()
        self.assertEqual(
            [{'body': '["http://xml.zeit.de/testcontent2"]',
              'path': '/', 'verb': 'POST'}],
            self.layer['request_handler'].requests)

    def test_does_not_call_hook_when_exclude_matches(self):
        self.config = """<webhooks>
          <webhook url="http://localhost:%s">
            <exclude>
              <type>testcontenttype</type>
            </exclude>
          </webhook>
        </webhooks>
        """ % self.layer['http_port']
        with checked_out(self.repository['testcontent']):
            pass
        self.assertEqual([], self.layer['request_handler'].requests)


class WebhookExcludeTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_match_contenttype(self):
        hook = zeit.cms.checkout.webhook.Hook(None)
        hook.add_exclude('type', 'testcontenttype')
        self.assertTrue(hook.should_exclude(self.repository['testcontent']))
        self.assertFalse(hook.should_exclude(self.repository['politik.feed']))

    def test_match_product(self):
        hook = zeit.cms.checkout.webhook.Hook(None)
        hook.add_exclude('product', 'ZEI')
        self.assertFalse(hook.should_exclude(self.repository['testcontent']))
        with checked_out(self.repository['testcontent']) as co:
            co.product = Product('ZEI')
        self.assertTrue(hook.should_exclude(self.repository['testcontent']))
