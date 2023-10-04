# coding: utf-8
from unittest import mock
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import os
import pytest
import time
import zeit.push.facebook
import zeit.push.interfaces
import zeit.push.testing
import zope.component


@pytest.mark.integration()
class FacebookTest(zeit.push.testing.TestCase):

    level = 2

    def setUp(self):
        super().setUp()
        # Page access token for
        # <https://www.facebook.com/pages/Vivi-Test/721128357931123>,
        # created on 2014-07-16, expires in about 60 days, recreate with
        # ./work/maintenancejobs/bin/facebook-access-token
        self.access_token = os.environ['ZEIT_PUSH_FACEBOOK_ACCESS_TOKEN']

        self.api = zeit.push.facebook.Connection(
            os.environ['ZEIT_PUSH_FACEBOOK_URL'])
        # repr keeps all digits  while str would cut them.
        self.nugget = repr(time.time())

    # Only relevant for the test_send_posts_status test
    def tearDown(self):
        for status in self.api._request(
                'GET', '/me/feed', self.access_token)['data']:
            if self.nugget in status.get('message', ''):
                self.api._request(
                    'DELETE', f'/{status["id"]}', self.access_token)
        super().tearDown()

    def test_send_posts_status(self):
        with mock.patch(
             'zeit.push.interfaces.FacebookAccountSource.access_token') as tok:
            tok.return_value = self.access_token
            self.api.send(
                'zeit.push.tests.faceboök %s' % self.nugget,
                'http://example.com', account='fb-test')

        for status in self.api._request(
                'GET', '/me/feed', self.access_token)['data']:
            if self.nugget in status['message']:
                self.assertIn('faceboök', status['message'])
                link = self.api._request(
                    'GET', f'/{status["id"]}/attachments', self.access_token)
                self.assertIn('example.com', link['data'][0]['target']['url'])
                break
        else:
            self.fail('Status was not posted')

    def test_errors_should_raise(self):
        with self.assertRaises(zeit.push.interfaces.TechnicalError) as e:
            self.api.send('foo', '', account='fb_ressort_deutschland')
        self.assertIn('Invalid OAuth access token', str(e.exception))


class FacebookAccountsTest(zeit.push.testing.TestCase):

    def test_main_account_is_excluded_from_source(self):
        self.assertEqual(
            ['fb-magazin', 'fb-campus', 'fb-zett'],
            list(zeit.push.interfaces.facebookAccountSource(None)))


class FacebookMessageTest(zeit.push.testing.TestCase):

    def test_uses_facebook_override_text(self):
        content = ExampleContentType()
        self.repository['foo'] = content
        push = zeit.push.interfaces.IPushMessages(content)
        push.message_config = [{
            'type': 'facebook', 'enabled': True, 'account': 'fb-test',
            'override_text': 'facebook'}]
        message = zope.component.getAdapter(
            content, zeit.push.interfaces.IMessage, name='facebook')
        # XXX This API is a bit unwieldy
        # (see zeit.push.workflow.PushMessages._create_message)
        message.config = push.message_config[0]
        self.assertEqual('facebook', message.text)

    def test_adds_campaign_parameters_to_url(self):
        content = self.repository['testcontent']
        message = zope.component.getAdapter(
            content, zeit.push.interfaces.IMessage, name='facebook')
        self.assertIn('wt_zmc=sm.int.zonaudev.facebook', message.url)
