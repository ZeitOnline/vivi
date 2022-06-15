# coding: utf-8
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import fb
import os
import time
import zeit.push.facebook
import zeit.push.interfaces
import zeit.push.testing
import zope.component
import requests


class FacebookTest(zeit.push.testing.TestCase):

    level = 2

    def setUp(self):
        # Page access token for
        # <https://www.facebook.com/pages/Vivi-Test/721128357931123>,
        # created on 2014-07-16, expires in about 60 days, recreate with
        # ./work/maintenancejobs/bin/facebook-access-token
        self.access_token = os.environ['ZEIT_PUSH_FACEBOOK_ACCESS_TOKEN']

        self.api = fb.graph.api(self.access_token)
        # repr keeps all digits  while str would cut them.
        self.nugget = repr(time.time())

        URL = 'https://graph.facebook.com?access_token=' + self.access_token
        self.current_api_version = float(
            requests.head(URL).headers['facebook-api-version'][1:])

    # Only relevant for the test_send_posts_status test
    def tearDown(self):
        for status in self.api.get_object(
                cat='single', id='me', fields=['feed'])['feed']['data']:
            if 'message' in status and self.nugget in status['message']:
                self.api.delete(id=status['id'])

    def test_send_posts_status(self):
        facebook = zeit.push.facebook.Connection()
        facebook.send(
            'zeit.push.tests.faceboök %s' % self.nugget, 'http://example.com',
            account='fb-test')

        for status in self.api.get_object(
                cat='single', id='me', fields=['feed'])['feed']['data']:

            if self.nugget in status['message']:
                post_id = status['id']

                fields = ['message', 'attachments']
                status = self.api.get_object(
                    cat='single', id=post_id, fields=fields)

                self.assertIn('example.com', status[
                    'attachments']['data'][0]['target']['url'])

                self.assertIn('faceboök', status['message'])
                break
        else:
            self.fail('Status was not posted')

    def test_errors_should_raise(self):
        facebook = zeit.push.facebook.Connection()
        with self.assertRaises(zeit.push.interfaces.TechnicalError) as e:
            facebook.send('foo', '', account='fb_ressort_deutschland')
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

    def test_breaking_flag_is_removed_from_service_after_send(self):
        content = ExampleContentType()
        self.repository['foo'] = content
        push = zeit.push.interfaces.IPushMessages(content)
        push.message_config = ({
            'type': 'facebook', 'enabled': True, 'breaking_news': True,
            'override_text': 'facebook'},)
        IPublishInfo(content).urgent = True
        IPublish(content).publish()
        self.assertEqual(
            ({'type': 'facebook', 'enabled': False, 'breaking_news': False,
              'override_text': 'facebook'},),
            push.message_config)
