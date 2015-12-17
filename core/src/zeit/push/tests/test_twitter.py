# coding: utf-8
import gocept.testing.assertion
import time
import tweepy
import zeit.push.interfaces
import zeit.push.testing
import zeit.push.twitter


class TwitterTest(zeit.push.testing.TestCase,
                  gocept.testing.assertion.String):

    level = 2

    # User: gocepttest
    # Pass: 9QuecCyewip0
    # Email: ws+twitter@gocept.com
    api_key = 'GwK5gIOXUG4JnKWjOOVXFmDr0'
    api_secret = 'Z2zrg2QYZAY2wEVqcG5smZOxdHCX0eo9SLkutb8aRljxVvG4sB'
    access_token = '2512010726-zzomC6jSp453N4Hsn7Ji3hYirt0a35sV0uL8Dy3'
    access_secret = 'DiVzrTRkh5YJCJztiqCCwXBIzGlqa1q7Zi1bDB8aASYOj'

    # User: gocepttest2
    # Pass: dalvEwjarph2
    # Email: ws+twitter2@gocept.com
    # access_token = '2734252303-ly3KyZ6BvlV6lhkvnhCX3bJZ35Rq91LPprSRVcm'
    # access_secret = 'DwZudWx0ao27sotLrvXSo9qD2YHgG1Et9giROopLSPhDt'

    def setUp(self):
        auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
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
            u'zeit.push.tests.ümläut.twitter %s' % self.nugget,
            'http://example.com',
            account='twitter-test')

        for status in self.api.home_timeline():
            if self.nugget in status.text:
                self.assertStartsWith(
                    u'zeit.push.tests.ümläut.twitter %s' % self.nugget,
                    status.text)
                break
        else:
            self.fail('Tweet was not posted')

    def test_errors_should_raise_appropriate_exception(self):
        twitter = zeit.push.twitter.Connection(
            self.api_key, self.api_secret)
        with self.assertRaises(zeit.push.interfaces.WebServiceError) as e:
            twitter.send('a' * 150, '', account='twitter-test')
        self.assertIn('Status is over 140 characters', e.exception.message)


class TwitterAccountsTest(zeit.push.testing.TestCase):

    def test_main_account_is_excluded_from_source(self):
        self.assertEqual(
            ['twitter_ressort_wissen', 'twitter_ressort_politik'],
            list(zeit.push.interfaces.twitterAccountSource(None)))
