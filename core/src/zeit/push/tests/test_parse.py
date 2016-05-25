from datetime import datetime
from zeit.cms.checkout.helper import checked_out
from zeit.push.interfaces import PARSE_NEWS_CHANNEL
import mock
import os
import pytz
import unittest
import urlparse
import zeit.push.parse
import zeit.push.testing
import zope.app.appsetup.product


class ParseTest(unittest.TestCase):

    level = 2

    def setUp(self):
        self.app_id = os.environ['ZEIT_PUSH_PARSE_APP_ID']
        self.api_key = os.environ['ZEIT_PUSH_PARSE_API_KEY']

    def test_push_works(self):
        # Parse offers no REST API to retrieve push messages,
        # so this is just a smoke test.
        api = zeit.push.parse.Connection(
            self.app_id, self.api_key, 1)
        api.send('Being pushy.', 'http://example.com', skip_ios=True)

    def test_push_works_with_channels(self):
        api = zeit.push.parse.Connection(
            self.app_id, self.api_key, 1)
        api.send('Being pushy.', 'http://example.com', channels=['News'],
                 skip_ios=True)

    def test_invalid_credentials_should_raise(self):
        api = zeit.push.parse.Connection('invalid', 'invalid', 1)
        with self.assertRaises(zeit.push.interfaces.WebServiceError):
            api.send('Being pushy.', 'http://example.com')

    def test_friedbert_version_links_to_app_content(self):
        api = zeit.push.parse.Connection(None, None, 1)
        with mock.patch.object(api, 'push') as push:
            api.send('', 'http://www.zeit.de/bar', channels=PARSE_NEWS_CHANNEL)
            android = push.call_args_list[0][0][0]
            self.assertEqual(
                'http://www.zeit.de/bar',
                android['data']['url'].split('?')[0])
            ios = push.call_args_list[1][0][0]
            self.assertEqual(
                'http://www.zeit.de/bar',
                ios['data']['aps']['url'].split('?')[0])


class RewriteWrapperURLTest(unittest.TestCase):

    target_host = 'http://wrapper.zeit.de'

    def rewrite(self, url):
        return zeit.push.parse.Connection.rewrite_url(url, self.target_host)

    def test_www_zeit_de_is_replaced_with_wrapper(self):
        self.assertEqual(
            self.target_host + '/foo/bar',
            self.rewrite('http://www.zeit.de/foo/bar'))

    def test_blog_zeit_de_is_replaced_with_wrapper_and_appends_query(self):
        self.assertEqual(
            self.target_host + '/blog/foo/bar?feed=articlexml',
            self.rewrite('http://blog.zeit.de/foo/bar'))

    def test_zeit_de_blog_is_replaced_with_wrapper_and_appends_query(self):
        self.assertEqual(
            self.target_host + '/blog/foo/bar?feed=articlexml',
            self.rewrite('http://www.zeit.de/blog/foo/bar'))

    def test_adds_tracking_information_as_query_string(self):
        url = zeit.push.parse.Connection.rewrite_url(
            'http://www.zeit.de/foo/bar', self.target_host)
        url = zeit.push.parse.Connection.add_tracking(
            url, 'nonbreaking', 'android')
        qs = urlparse.parse_qs(urlparse.urlparse(url).query)
        self.assertEqual(
            'fix.int.zonaudev.push.wichtige_news.zeitde.andpush.link.x',
            qs['wt_zmc'][0])
        self.assertEqual('zeitde_andpush_link_x', qs['utm_content'][0])
        self.assertEqual('push_zonaudev_int', qs['utm_source'][0])
        self.assertEqual('wichtige_news', qs['utm_campaign'][0])
        self.assertEqual('fix', qs['utm_medium'][0])

    def test_adds_tracking_information_blog(self):
        url = zeit.push.parse.Connection.rewrite_url(
            'http://www.zeit.de/blog/foo/bar', self.target_host)
        url = zeit.push.parse.Connection.add_tracking(
            url, 'nonbreaking', 'android')
        qs = urlparse.parse_qs(urlparse.urlparse(url).query)
        self.assertEqual('articlexml', qs['feed'][0])
        self.assertEqual('push_zonaudev_int', qs['utm_source'][0])


class RewriteFriedbertURLTest(RewriteWrapperURLTest):

    target_host = 'http://app-content.zeit.de'


class ParametersTest(zeit.push.testing.TestCase):

    def create_catalog(self):
        domain = zope.i18n.translationdomain.TranslationDomain('zeit.cms')
        self.zca.patch_utility(domain, name='zeit.cms')
        self.catalog = zeit.cms.testing.TestCatalog()
        domain.addCatalog(self.catalog)

    def test_sets_expiration_time(self):
        api = zeit.push.parse.Connection(
            'any', 'any', 3600)
        with mock.patch('zeit.push.parse.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(
                2014, 07, 1, 10, 15, 7, 38, tzinfo=pytz.UTC)
            with mock.patch.object(api, 'push') as push:
                api.send('foo', 'any')
                data = push.call_args[0][0]
                self.assertEqual(
                    '2014-07-01T11:15:07+00:00', data['expiration_time'])

    def test_no_channels_given_omits_channels_parameter(self):
        api = zeit.push.parse.Connection(
            'any', 'any', 1)
        with mock.patch.object(api, 'push') as push:
            api.send('foo', 'any')
            data = push.call_args[0][0]
            self.assertNotIn('channels', data['where'])

    def test_channels_string_is_looked_up_in_product_config(self):
        product_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.push')
        product_config['foo'] = 'bar qux'
        api = zeit.push.parse.Connection(
            'any', 'any', 1)
        with mock.patch.object(api, 'push') as push:
            api.send('foo', 'any', channels='foo')
            data = push.call_args[0][0]
            self.assertEqual(['bar', 'qux'], data['where']['channels']['$in'])

    def test_aa_empty_product_config_omits_channels_parameter(self):
        product_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.push')
        product_config['foo'] = ''
        api = zeit.push.parse.Connection(
            'any', 'any', 1)
        with mock.patch.object(api, 'push') as push:
            api.send('foo', 'any', channels='foo')
            data = push.call_args[0][0]
            self.assertNotIn('channels', data['where'])

    def test_translates_title(self):
        self.create_catalog()
        self.catalog.messages['parse-breaking-title'] = 'foo'
        api = zeit.push.parse.Connection(
            'any', 'any', 1)
        api.LANGUAGE = 'tt'
        with mock.patch.object(api, 'push') as push:
            api.send('foo', 'any')
            data = push.call_args[0][0]
            self.assertEqual('foo', data['data']['aps']['alert-title'])

    def test_transmits_metadata(self):
        self.create_catalog()
        self.catalog.messages['parse-news-title'] = 'ZEIT ONLINE'

        api = zeit.push.parse.Connection(
            'any', 'any', 1)
        api.LANGUAGE = 'tt'
        with mock.patch.object(api, 'push') as push:
            api.send('foo', 'any', channels=PARSE_NEWS_CHANNEL,
                     teaserSupertitle='super', teaserTitle='title',
                     teaserText='teaser', override_text=None,
                     image_url='http://images.zeit.de/example')
            android = push.call_args_list[0][0][0]
            self.assertEqual('title', android['data']['text'])
            self.assertEqual('teaser', android['data']['teaser'])
            self.assertEqual(
                'http://images.zeit.de/example', android['data']['imageUrl'])
            ios = push.call_args_list[1][0][0]
            self.assertEqual('super', ios['data']['aps']['headline'])
            self.assertEqual('ZEIT ONLINE', ios['data']['aps']['alert-title'])
            self.assertEqual('title', ios['data']['aps']['alert'])
            self.assertEqual('teaser', ios['data']['aps']['teaser'])
            self.assertEqual(
                'http://images.zeit.de/example',
                ios['data']['aps']['imageUrl'])

    def test_message_config_may_override_text(self):
        api = zeit.push.parse.Connection(
            'any', 'any', 1)
        with mock.patch.object(api, 'push') as push:
            api.send('foo', 'any', channels=PARSE_NEWS_CHANNEL,
                     override_text='mytext', teaserTitle='title',
                     image_url='http://images.zeit.de/example')
            android = push.call_args_list[0][0][0]
            self.assertEqual('mytext', android['data']['text'])
            ios = push.call_args_list[1][0][0]
            self.assertEqual('mytext', ios['data']['aps']['alert'])


class PushNewsFlagTest(zeit.push.testing.TestCase):

    def test_sets_flag_on_checkin(self):
        content = self.repository['testcontent']
        self.assertFalse(content.push_news)
        with checked_out(content) as co:
            push = zeit.push.interfaces.IPushMessages(co)
            push.enabled = True
            push.message_config = ({
                'type': 'parse', 'enabled': True,
                'channels': PARSE_NEWS_CHANNEL,
            },)
        content = self.repository['testcontent']
        self.assertTrue(content.push_news)
