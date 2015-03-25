from datetime import datetime
from zeit.cms.checkout.helper import checked_out
from zeit.push.interfaces import PARSE_NEWS_CHANNEL, PARSE_BREAKING_CHANNEL
from zeit.push.testing import parse_settings as settings
import mock
import pytz
import unittest
import zeit.push.parse
import zeit.push.testing
import zope.app.appsetup.product


class ParseTest(unittest.TestCase):

    level = 2

    def test_push_works(self):
        # Parse offers no REST API to retrieve push messages,
        # so this is just a smoke test.
        api = zeit.push.parse.Connection(
            settings['application_id'], settings['rest_api_key'], 1)
        api.send('Being pushy.', 'http://example.com', skip_ios=True)

    def test_push_works_with_channels(self):
        api = zeit.push.parse.Connection(
            settings['application_id'], settings['rest_api_key'], 1)
        api.send('Being pushy.', 'http://example.com', channels=['News'],
                 skip_ios=True)

    def test_invalid_credentials_should_raise(self):
        api = zeit.push.parse.Connection('invalid', 'invalid', 1)
        with self.assertRaises(zeit.push.interfaces.WebServiceError):
            api.send('Being pushy.', 'http://example.com')

    def test_channel_breaking_is_pushed_to_all_supporting_app_versions(self):
        api = zeit.push.parse.Connection(None, None, 1)
        with mock.patch.object(api, 'push') as push:
            api.send('Foo', 'http://b.ar', channels=PARSE_BREAKING_CHANNEL)
            assert len(push.call_args_list) == 4

    def test_channel_news_is_pushed_to_all_supporting_app_versions(self):
        api = zeit.push.parse.Connection(None, None, 1)
        with mock.patch.object(api, 'push') as push:
            api.send('Foo', 'http://b.ar', channels=PARSE_NEWS_CHANNEL)
            assert len(push.call_args_list) == 2


class URLRewriteTest(unittest.TestCase):

    def rewrite(self, url):
        return zeit.push.parse.Connection.rewrite_url(url)

    def test_www_zeit_de_is_replaced_with_wrapper(self):
        self.assertEqual(
            'http://wrapper.zeit.de/foo/bar',
            self.rewrite('http://www.zeit.de/foo/bar'))

    def test_blog_zeit_de_is_replaced_with_wrapper_and_appends_query(self):
        self.assertEqual(
            'http://wrapper.zeit.de/blog/foo/bar?feed=articlexml',
            self.rewrite('http://blog.zeit.de/foo/bar'))

    def test_zeit_de_blog_is_replaced_with_wrapper_and_appends_query(self):
        self.assertEqual(
            'http://wrapper.zeit.de/blog/foo/bar?feed=articlexml',
            self.rewrite('http://www.zeit.de/blog/foo/bar'))


class ParametersTest(zeit.push.testing.TestCase):

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
        domain = zope.i18n.translationdomain.TranslationDomain('zeit.cms')
        self.zca.patch_utility(domain, name='zeit.cms')
        self.catalog = zeit.cms.testing.TestCatalog()
        domain.addCatalog(self.catalog)
        self.catalog.messages['breaking-news-parse-title'] = 'foo'
        api = zeit.push.parse.Connection(
            'any', 'any', 1)
        api.LANGUAGE = 'tt'
        with mock.patch.object(api, 'push') as push:
            api.send('foo', 'any')
            data = push.call_args[0][0]
            self.assertEqual('foo', data['data']['aps']['alert-title'])

    def test_transmits_metadata(self):
        api = zeit.push.parse.Connection(
            'any', 'any', 1)
        with mock.patch.object(api, 'push') as push:
            api.send('foo', 'any', channels=PARSE_NEWS_CHANNEL,
                     supertitle='super', teaserText='teaser')
            payload = push.call_args_list[0][0][0]
            self.assertEqual('super', payload['data']['headline'])
            self.assertEqual('teaser', payload['data']['teaser'])


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
