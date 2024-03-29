# coding: utf-8
import os
import time
import unittest

import gocept.testing.assertion
import plone.testing.zca
import pytest
import zope.component

from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.push.interfaces
import zeit.push.testing
import zeit.push.twitter


@unittest.skip('Twitter API v2 is currently very flaky')
@pytest.mark.integration()
class TwitterTest(unittest.TestCase, gocept.testing.assertion.String):
    level = 2

    def setUp(self):
        plone.testing.zca.pushGlobalRegistry()
        zope.component.getSiteManager().registerUtility(zeit.push.testing.TwitterCredentials())

        self.client_id = os.environ['ZEIT_PUSH_TWITTER_API_KEY']
        self.client_secret = os.environ['ZEIT_PUSH_TWITTER_API_SECRET']
        self.api = zeit.push.twitter.TwitterClient(
            self.client_id, self.client_secret, 'twitter-test'
        )
        # repr keeps all digits  while str would cut them.
        self.nugget = repr(time.time())

    def tearDown(self):
        for status in self.api.get_home_timeline().data:
            if self.nugget in status.text:
                self.api.delete_tweet(status.id)
        plone.testing.zca.popGlobalRegistry()

    def test_send_posts_twitter_status(self):
        twitter = zeit.push.twitter.Connection(self.client_id, self.client_secret)
        twitter.send(
            'zeit.push.tests.ümläut.twitter %s' % self.nugget,
            'http://example.com',
            account='twitter-test',
        )

        time.sleep(30)  # Don't poll, so we avoid rather tight API rate limits
        for status in self.api.get_home_timeline().data:
            if self.nugget in status.text:
                self.assertStartsWith(
                    'zeit.push.tests.ümläut.twitter %s' % self.nugget, status.text
                )
                break
        else:
            self.fail('Tweet was not posted')

    def test_errors_should_raise_appropriate_exception(self):
        twitter = zeit.push.twitter.Connection(self.client_id, self.client_secret)
        with self.assertRaises(zeit.push.interfaces.WebServiceError) as e:
            twitter.send('a' * 350, '', account='twitter-test')
        self.assertIn('Tweet needs to be a bit shorter', str(e.exception))


class TwitterAccountsTest(zeit.push.testing.TestCase):
    def test_main_account_is_excluded_from_source(self):
        self.assertEqual(
            ['twitter_ressort_wissen', 'twitter_ressort_politik'],
            list(zeit.push.interfaces.twitterAccountSource(None)),
        )


class TwitterMessageTest(zeit.push.testing.TestCase):
    def test_uses_twitter_ressort_override_text(self):
        content = ExampleContentType()
        self.repository['foo'] = content
        push = zeit.push.interfaces.IPushMessages(content)
        push.message_config = [
            {
                'type': 'twitter',
                'account': 'twitter_ressort_wissen',
                'variant': 'ressort',
                'enabled': True,
                'override_text': 'foobar',
            }
        ]
        message = zope.component.getAdapter(content, zeit.push.interfaces.IMessage, name='twitter')
        # XXX This API is a bit unwieldy
        # (see zeit.push.workflow.PushMessages._create_message)
        message.config = push.message_config[0]
        self.assertEqual('foobar', message.text)

    def test_adds_campaign_parameters_to_url(self):
        content = self.repository['testcontent']
        message = zope.component.getAdapter(content, zeit.push.interfaces.IMessage, name='twitter')
        self.assertIn('wt_zmc=sm.int.zonaudev.twitter', message.url)
