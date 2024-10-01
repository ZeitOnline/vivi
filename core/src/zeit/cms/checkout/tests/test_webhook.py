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
import zeit.cms.workflow.interfaces


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
          <webhook id="add" url="http://localhost:{port}"/>
          <webhook id="checkin" url="http://localhost:{port}"/>
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
          <webhook id="checkin" url="http://localhost:{port}">
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

    def test_match_product_attribute(self):
        hook = zeit.cms.checkout.webhook.Hook('checkin', None)
        hook.add_exclude('product_counter', 'online')
        self.assertFalse(hook.should_exclude(self.repository['testcontent']))
        with checked_out(self.repository['testcontent']) as co:
            co.product = Product('ZEDE')
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


class WebhookIncludeTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_matches_criteria_is_false_when_include_does_not_match_contenttype(self):
        hook = zeit.cms.checkout.webhook.Hook(None, None)
        hook.add_include('type', 'testcontenttype')
        self.assertTrue(hook.should_include(self.repository['testcontent']))
        self.assertFalse(hook.should_include(self.repository['online']['2007']['01']['Somalia']))

    def test_matches_criteria_is_false_when_include_does_not_match(self):
        hook = zeit.cms.checkout.webhook.Hook(None, None)
        hook.add_include('type', 'wrong-content-type')
        self.assertFalse(hook.matches_criteria(self.repository['testcontent']))


class WebhookExcludeStrongerThanIncludeTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_exclude_weighs_more_than_include_on_same_attribute(self):
        hook = zeit.cms.checkout.webhook.Hook(None, None)
        hook.add_include('type', 'testcontenttype')
        hook.add_exclude('type', 'testcontenttype')
        self.assertFalse(hook.matches_criteria(self.repository['testcontent']))

    def test_exclude_weighs_more_than_include_on_different_attribute(self):
        hook = zeit.cms.checkout.webhook.Hook('checkin', None)
        hook.add_include('type', 'testcontenttype')
        hook.add_exclude('product_counter', 'online')
        self.assertTrue(hook.matches_criteria(self.repository['testcontent']))
        with checked_out(self.repository['testcontent']) as co:
            co.product = Product('ZEDE')
        self.assertFalse(hook.matches_criteria(self.repository['testcontent']))


class WebhookEventTest(FunctionalTestCase):
    @property
    def config(self):
        port = self.layer['http_port']
        return f"""<webhooks>
          <webhook id="add" url="http://localhost:{port}"/>
          <webhook id="checkin" url="http://localhost:{port}">
            <exclude>
              <product_counter>online</product_counter>
            </exclude>
          </webhook>
          <webhook id="publish" url="http://localhost:{port}">
            <exclude>
              <product_counter>print</product_counter>
            </exclude>
          </webhook>
          <!-- this webhook will be excluded, see exclude type = testconttype -->
          <webhook id="publish" url="http://localhost/two:{port}">
            <include>
              <product_counter>print</product_counter>
            </include>
            <exclude>
              <type>testcontenttype</type>
            </exclude>
          </webhook>
        </webhooks>
        """

    def test_webhook_is_only_notified_on_checkin(self):
        with checked_out(self.repository['testcontent']) as co:
            co.product = Product('ZEI')
            info = zeit.cms.workflow.interfaces.IPublishInfo(co)
            info.urgent = True
        workflow = zeit.cms.workflow.interfaces.IPublish(self.repository['testcontent'])
        workflow.publish()
        requests = self.layer['request_handler'].requests
        self.assertEqual(1, len(requests))

    def test_webhook_is_not_notified_on_checkin(self):
        with checked_out(self.repository['testcontent']) as co:
            co.product = Product('ZEDE')
        requests = self.layer['request_handler'].requests
        self.assertEqual(0, len(requests))

    def test_webhook_is_only_notified_on_publish(self):
        with checked_out(self.repository['testcontent']) as co:
            co.product = Product('ZEDE')
            info = zeit.cms.workflow.interfaces.IPublishInfo(co)
            info.urgent = True
        workflow = zeit.cms.workflow.interfaces.IPublish(self.repository['testcontent'])
        workflow.publish()
        requests = self.layer['request_handler'].requests
        self.assertEqual(1, len(requests))
        request = requests[0]
        del request['headers']
        self.assertEqual(
            {'body': '["http://xml.zeit.de/testcontent"]', 'path': '/', 'verb': 'POST'}, request
        )

    def test_webhook_is_notified_on_add_and_checkin_and_not_on_publish(self):
        self.repository['testcontent2'] = ExampleContentType()
        with checked_out(self.repository['testcontent2']) as co:
            co.product = Product('ZEI')
        requests = self.layer['request_handler'].requests
        self.assertEqual(2, len(requests))

    def test_webhook_is_notified_on_add_and_publish_and_not_on_checkin(self):
        self.repository['testcontent2'] = ExampleContentType()
        with checked_out(self.repository['testcontent2']) as co:
            co.product = Product('ZEDE')
            info = zeit.cms.workflow.interfaces.IPublishInfo(co)
            info.urgent = True
        workflow = zeit.cms.workflow.interfaces.IPublish(self.repository['testcontent'])
        workflow.publish()
        requests = self.layer['request_handler'].requests
        self.assertEqual(2, len(requests))


class TestMultipleWebhooksWithSameId(FunctionalTestCase):
    @property
    def config(self):
        port = self.layer['http_port']
        return f"""<webhooks>
              <webhook id="publish" url="http://localhost/one:{port}">
                <include>
                  <product_counter>print</product_counter>
                </include>
              </webhook>
              <webhook id="publish" url="http://localhost/two:{port}">
                <include>
                  <product_counter>print</product_counter>
                </include>
              </webhook>
              <webhook id="publish" url="http://localhost/three:{port}">
                <include>
                  <product_counter>print</product_counter>
                </include>
              </webhook>
              <!-- this test should be excluded, see exclude -->
              <webhook id="publish" url="http://localhost/four:{port}">
                <include>
                  <product_counter>print</product_counter>
                </include>
                <exclude>
                  <type>testcontenttype</type>
                </exclude>
              </webhook>
            </webhooks>
            """

    def test_multiple_webhooks_with_same_id(self):
        requests_post_mock = mock.patch('requests.post').start()

        with checked_out(self.repository['testcontent']) as co:
            co.product = Product('ZEI')
            info = zeit.cms.workflow.interfaces.IPublishInfo(co)
            info.urgent = True
        workflow = zeit.cms.workflow.interfaces.IPublish(self.repository['testcontent'])
        workflow.publish()

        # Only 3 requests should match, the last one is excluded.
        self.assertEqual(3, requests_post_mock.call_count)

        # check if all url's match
        expected_urls = [
            f'http://localhost/one:{self.layer["http_port"]}',
            f'http://localhost/two:{self.layer["http_port"]}',
            f'http://localhost/three:{self.layer["http_port"]}',
        ]
        actual_urls = [call.args[0] for call in requests_post_mock.call_args_list]
        for url in expected_urls:
            self.assertIn(url, actual_urls)

        mock.patch.stopall()
