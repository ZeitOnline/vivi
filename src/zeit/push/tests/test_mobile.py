from datetime import datetime
from zeit.cms.checkout.helper import checked_out
from zeit.push.interfaces import PARSE_NEWS_CHANNEL
import mock
import pytz
import unittest
import urlparse
import zeit.cms.testing
import zeit.push.interfaces
import zeit.push.mobile
import zeit.push.testing
import zope.app.appsetup.product
import zope.i18n.translationdomain


class ParametersTest(zeit.push.testing.TestCase):

    def create_catalog(self):
        domain = zope.i18n.translationdomain.TranslationDomain('zeit.cms')
        self.zca.patch_utility(domain, name='zeit.cms')
        catalog = zeit.cms.testing.TestCatalog()
        domain.addCatalog(catalog)
        return catalog

    def test_calculates_expiration_datetime_based_on_expire_interval(self):
        api = zeit.push.mobile.ConnectionBase('any', 'any', 3600)
        with mock.patch('zeit.push.mobile.datetime') as mock_datetime:
            mock_datetime.now.return_value = (
                datetime(2014, 07, 1, 10, 15, 7, 38, tzinfo=pytz.UTC))
            self.assertEqual(
                datetime(2014, 07, 1, 11, 15, 7, 0, tzinfo=pytz.UTC),
                api.expiration_datetime)

    def test_channels_string_is_looked_up_in_product_config(self):
        product_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.push')
        product_config['foo'] = 'bar qux'
        api = zeit.push.mobile.ConnectionBase('any', 'any', 1)
        self.assertEqual(['bar', 'qux'], api.get_channel_list('foo'))

    def test_translates_title(self):
        catalog = self.create_catalog()
        catalog.messages['parse-breaking-title'] = 'foo'
        api = zeit.push.mobile.ConnectionBase('any', 'any', 1)
        api.LANGUAGE = 'tt'
        self.assertEqual('foo', api.get_headline([]))

    def test_transmits_metadata(self):
        catalog = self.create_catalog()
        catalog.messages['parse-news-title'] = 'ZEIT ONLINE'

        api = zeit.push.mobile.ConnectionBase('any', 'any', 1)
        api.LANGUAGE = 'tt'
        data = api.data('foo', 'any', channels=PARSE_NEWS_CHANNEL,
                        teaserSupertitle='super', teaserTitle='title',
                        teaserText='teaser', override_text=None,
                        image_url='http://images.zeit.de/example')

        android = data['android']
        self.assertEqual('ZEIT ONLINE', android['headline'])
        self.assertEqual('title', android['text'])
        self.assertEqual('teaser', android['teaser'])
        self.assertEqual('http://images.zeit.de/example', android['imageUrl'])

        ios = data['ios']
        self.assertEqual('super', ios['headline'])
        self.assertEqual('ZEIT ONLINE', ios['alert-title'])
        self.assertEqual('title', ios['alert'])
        self.assertEqual('teaser', ios['teaser'])
        self.assertEqual('http://images.zeit.de/example', ios['imageUrl'])

    def test_message_config_may_override_text(self):
        api = zeit.push.mobile.ConnectionBase('any', 'any', 1)
        data = api.data('foo', 'any', override_text='mytext')
        self.assertEqual('mytext', data['android']['text'])
        self.assertEqual('mytext', data['ios']['alert'])


class RewriteURLTest(unittest.TestCase):

    target_host = 'http://www.staging.zeit.de'

    def rewrite(self, url):
        return zeit.push.mobile.ConnectionBase.rewrite_url(
            url, self.target_host)

    def test_www_zeit_de_is_replaced_with_staging(self):
        self.assertEqual(
            self.target_host + '/foo/bar',
            self.rewrite('http://www.zeit.de/foo/bar'))

    def test_blog_zeit_de_is_replaced_with_staging_and_appends_query(self):
        self.assertEqual(
            self.target_host + '/blog/foo/bar?feed=articlexml',
            self.rewrite('http://blog.zeit.de/foo/bar'))

    def test_zeit_de_blog_is_replaced_with_staging_and_appends_query(self):
        self.assertEqual(
            self.target_host + '/blog/foo/bar?feed=articlexml',
            self.rewrite('http://www.zeit.de/blog/foo/bar'))

    def test_adds_tracking_information_as_query_string(self):
        url = zeit.push.mobile.ConnectionBase.rewrite_url(
            'http://www.zeit.de/foo/bar', self.target_host)
        url = zeit.push.mobile.ConnectionBase.add_tracking(
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
        url = zeit.push.mobile.ConnectionBase.rewrite_url(
            'http://www.zeit.de/blog/foo/bar', self.target_host)
        url = zeit.push.mobile.ConnectionBase.add_tracking(
            url, 'nonbreaking', 'android')
        qs = urlparse.parse_qs(urlparse.urlparse(url).query)
        self.assertEqual('articlexml', qs['feed'][0])
        self.assertEqual('push_zonaudev_int', qs['utm_source'][0])


class PushNewsFlagTest(zeit.push.testing.TestCase):

    def test_sets_flag_on_checkin(self):
        content = self.repository['testcontent']
        self.assertFalse(content.push_news)
        with checked_out(content) as co:
            push = zeit.push.interfaces.IPushMessages(co)
            push.message_config = ({
                'type': 'mobile', 'enabled': True,
                'channels': PARSE_NEWS_CHANNEL,
            },)
        content = self.repository['testcontent']
        self.assertTrue(content.push_news)
