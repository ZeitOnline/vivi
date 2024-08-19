from unittest import mock

import celery.exceptions
import lxml.etree
import plone.testing
import requests.exceptions

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.sources import Product
from zeit.cms.repository.interfaces import IAutomaticallyRenameable
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.checkout.webhook
import zeit.cms.testing


HTTP_LAYER = zeit.cms.testing.HTTPLayer(
    zeit.cms.testing.RecordingRequestHandler, name='HTTPLayer', module=__name__
)


WEBHOOK_LAYER = plone.testing.Layer(
    bases=(zeit.cms.testing.ZOPE_LAYER, HTTP_LAYER), name='WebhookLayer', module=__name__
)


class FunctionalTestCase(zeit.cms.testing.ZeitCmsTestCase):
    layer = WEBHOOK_LAYER

    @property
    def config(self):
        port = self.layer['http_port']
        return f"""<webhooks>
          <webhook id="default" url="http://localhost:{port}"/>
        </webhooks>
        """

    def setUp(self):
        super().setUp()
        self.patch = mock.patch(
            'zeit.cms.checkout.webhook.HookSource._get_tree',
            side_effect=lambda: lxml.etree.fromstring(self.config),
        )
        self.patch.start()
        source = zeit.cms.checkout.webhook.HOOKS.factory
        # XXX Have to pass the instance because of zc.factory init shenanigans.
        source._values.invalidate(source)

    def tearDown(self):
        self.patch.stop()
        super().tearDown()


class WebhookTest(FunctionalTestCase):
    def test_calls_post_with_uniqueId_for_configured_urls(self):
        with checked_out(self.repository['testcontent']):
            pass
        requests = self.layer['request_handler'].requests
        self.assertEqual(1, len(requests))
        request = requests[0]
        del request['headers']
        self.assertEqual(
            {'body': '["http://xml.zeit.de/testcontent"]', 'path': '/', 'verb': 'POST'}, request
        )

    def test_calls_hook_when_adding_new_object_to_repository(self):
        self.repository['testcontent2'] = ExampleContentType()
        requests = self.layer['request_handler'].requests
        self.assertEqual(1, len(requests))
        request = requests[0]
        del request['headers']
        self.assertEqual(
            {'body': '["http://xml.zeit.de/testcontent2"]', 'path': '/', 'verb': 'POST'}, request
        )

    def test_retry_on_technical_error(self):
        self.layer['request_handler'].response_code = [503, 200]
        with self.assertRaises(celery.exceptions.Retry):
            with checked_out(self.repository['testcontent']):
                pass

    def test_no_retry_on_semantic_error(self):
        self.layer['request_handler'].response_code = [400, 200]
        with self.assertRaises(requests.exceptions.HTTPError):
            with checked_out(self.repository['testcontent']):
                pass


class WebhookConfigTest(FunctionalTestCase):
    @property
    def config(self):
        port = self.layer['http_port']
        return f"""<webhooks>
          <webhook id="default" url="http://localhost:{port}">
            <exclude>
              <type>testcontenttype</type>
            </exclude>
          </webhook>
        </webhooks>
        """

    def test_does_not_call_hook_when_exclude_matches(self):
        with checked_out(self.repository['testcontent']):
            pass
        self.assertEqual([], self.layer['request_handler'].requests)


class WebhookExcludeTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_match_contenttype(self):
        hook = zeit.cms.checkout.webhook.Hook(None, None)
        hook.add_exclude('type', 'testcontenttype')
        self.assertTrue(hook.should_exclude(self.repository['testcontent']))
        self.assertFalse(hook.should_exclude(self.repository['online']['2007']['01']['Somalia']))

    def test_match_product(self):
        hook = zeit.cms.checkout.webhook.Hook(None, None)
        hook.add_exclude('product', 'ZEI')
        self.assertFalse(hook.should_exclude(self.repository['testcontent']))
        with checked_out(self.repository['testcontent']) as co:
            co.product = Product('ZEI')
        self.assertTrue(hook.should_exclude(self.repository['testcontent']))

    def test_skip_auto_renameable(self):
        hook = zeit.cms.checkout.webhook.Hook(None, None)
        self.assertFalse(hook.should_exclude(self.repository['testcontent']))
        with checked_out(self.repository['testcontent']) as co:
            IAutomaticallyRenameable(co).renameable = True
        self.assertTrue(hook.should_exclude(self.repository['testcontent']))

    def test_match_path_prefix(self):
        hook = zeit.cms.checkout.webhook.Hook(None, None)
        hook.add_exclude('path_prefix', '/online')
        self.assertFalse(hook.should_exclude(self.repository['testcontent']))
        self.assertTrue(hook.should_exclude(self.repository['online']['2007']['01']['Somalia']))
