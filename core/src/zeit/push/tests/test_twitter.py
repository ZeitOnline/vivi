# coding: utf-8
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import os
import time
import tweepy
import unittest
import zeit.push.interfaces
import zeit.push.testing
import zeit.push.twitter
import zope.component


@unittest.skip(
    'The free Twitter API level only allows writing tweets, not reading them')
class TwitterTest(zeit.push.testing.TestCase):

    level = 2

    def setUp(self):
        self.api_key = os.environ['ZEIT_PUSH_TWITTER_API_KEY']
        self.api_secret = os.environ['ZEIT_PUSH_TWITTER_API_SECRET']
        self.access_token = os.environ['ZEIT_PUSH_TWITTER_ACCESS_TOKEN']
        self.access_secret = os.environ['ZEIT_PUSH_TWITTER_ACCESS_SECRET']

        auth = tweepy.OAuth1UserHandler(self.api_key, self.api_secret)
        auth.set_access_token(self.access_token, self.access_secret)
        self.api = tweepy.API(auth)
        # repr keeps all digits  while str would cut them.
        self.nugget = repr(time.time())

    def tearDown(self):
        for status in self.api.home_timeline():
            if self.nugget in status.text:
                status.destroy()

    def test_send_posts_twitter_status(self):
        twitter = zeit.push.twitter.Connection(
            self.api_key, self.api_secret)
        twitter.send(
            'zeit.push.tests.ümläut.twitter %s' % self.nugget,
            'http://example.com',
            account='twitter-test')

        for status in self.api.home_timeline():
            if self.nugget in status.text:
                self.assertStartsWith(
                    'zeit.push.tests.ümläut.twitter %s' % self.nugget,
                    status.text)
                break
        else:
            self.fail('Tweet was not posted')

    def test_errors_should_raise_appropriate_exception(self):
        twitter = zeit.push.twitter.Connection(
            self.api_key, self.api_secret)
        with self.assertRaises(zeit.push.interfaces.WebServiceError) as e:
            twitter.send('a' * 350, '', account='twitter-test')
        self.assertIn('Tweet needs to be a bit shorter', str(e.exception))


class TwitterAccountsTest(zeit.push.testing.TestCase):

    def test_main_account_is_excluded_from_source(self):
        self.assertEqual(
            ['twitter_ressort_wissen', 'twitter_ressort_politik'],
            list(zeit.push.interfaces.twitterAccountSource(None)))


class TwitterMessageTest(zeit.push.testing.TestCase):

    def test_uses_twitter_ressort_override_text(self):
        content = ExampleContentType()
        self.repository['foo'] = content
        push = zeit.push.interfaces.IPushMessages(content)
        push.message_config = [{
            'type': 'twitter', 'account': 'twitter_ressort_wissen',
            'variant': 'ressort', 'enabled': True, 'override_text': 'foobar'}]
        message = zope.component.getAdapter(
            content, zeit.push.interfaces.IMessage, name='twitter')
        # XXX This API is a bit unwieldy
        # (see zeit.push.workflow.PushMessages._create_message)
        message.config = push.message_config[0]
        self.assertEqual('foobar', message.text)

    def test_adds_campaign_parameters_to_url(self):
        content = self.repository['testcontent']
        message = zope.component.getAdapter(
            content, zeit.push.interfaces.IMessage, name='twitter')
        self.assertIn('wt_zmc=sm.int.zonaudev.twitter', message.url)
