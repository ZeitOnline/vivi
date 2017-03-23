from datetime import datetime
from zeit.cms.checkout.helper import checked_out
from zeit.push.interfaces import CONFIG_CHANNEL_BREAKING, CONFIG_CHANNEL_NEWS
import mock
import pytz
import unittest
import urlparse
import zeit.cms.testing
import zeit.content.image.interfaces
import zeit.push.interfaces
import zeit.push.mobile
import zeit.push.testing
import zope.app.appsetup.product
import zope.component
import zope.i18n.translationdomain


class DataTest(zeit.push.testing.TestCase):

    def create_catalog(self):
        domain = zope.i18n.translationdomain.TranslationDomain('zeit.cms')
        self.zca.patch_utility(domain, name='zeit.cms')
        catalog = zeit.cms.testing.TestCatalog()
        domain.addCatalog(catalog)
        return catalog

    def test_calculates_expiration_datetime_based_on_expire_interval(self):
        api = zeit.push.mobile.ConnectionBase(3600)
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
        api = zeit.push.mobile.ConnectionBase(1)
        self.assertEqual(['bar', 'qux'], api.get_channel_list('foo'))

    def test_translates_title_based_on_channel(self):
        catalog = self.create_catalog()
        catalog.messages['push-news-title'] = 'bar'
        catalog.messages['push-breaking-title'] = 'foo'
        api = zeit.push.mobile.ConnectionBase(1)
        api.LANGUAGE = 'tt'
        self.assertEqual(None, api.get_headline(['News']))
        self.assertEqual('foo', api.get_headline(['Eilmeldung']))

    def test_transmits_news_metadata(self):
        catalog = self.create_catalog()
        catalog.messages['push-news-title'] = 'News'
        api = zeit.push.mobile.ConnectionBase(1)
        api.LANGUAGE = 'tt'
        data = api.data('foo', 'any', channels=CONFIG_CHANNEL_NEWS)

        android = data['android']
        self.assertEqual(None, android['headline'])
        self.assertEqual('foo', android['alert'])
        self.assertEqual(0, android['priority'])

        ios = data['ios']
        self.assertEqual(None, ios['headline'])
        self.assertEqual('foo', ios['alert'])
        self.assertEqual('', ios['sound'])

    def test_transmits_breaking_metadata(self):
        catalog = self.create_catalog()
        catalog.messages['push-breaking-title'] = 'Breaking'
        api = zeit.push.mobile.ConnectionBase(1)
        api.LANGUAGE = 'tt'
        data = api.data('bar', 'any', channels=CONFIG_CHANNEL_BREAKING)

        android = data['android']
        self.assertEqual('ZEIT ONLINE Breaking', android['headline'])
        self.assertEqual('bar', android['alert'])
        self.assertEqual(2, android['priority'])

        ios = data['ios']
        self.assertEqual('Breaking', ios['headline'])
        self.assertEqual('bar', ios['alert'])
        self.assertEqual('chime.aiff', ios['sound'])

    def test_www_url_is_replaced_with_staging(self):
        api = zeit.push.mobile.ConnectionBase(1)
        api.config['push-target-url'] = 'http://www.staging.zeit.de'
        data = api.data('', 'http://www.zeit.de/foo/bar')
        self.assertTrue(
            data['android']['url'].startswith(
                'http://www.staging.zeit.de/foo/bar'))
        self.assertTrue(
            data['ios']['url'].startswith(
                'http://www.staging.zeit.de/foo/bar'))

    def test_url_replacement_works_without_scheme(self):
        api = zeit.push.mobile.ConnectionBase(1)
        api.config['push-target-url'] = 'foo.zeit.de'
        data = api.data('', 'http://www.zeit.de/bar')
        self.assertTrue(
            data['android']['url'].startswith(
                'foo.zeit.de/bar'))
        self.assertTrue(
            data['ios']['url'].startswith(
                'foo.zeit.de/bar'))

    def test_url_replacement_works_with_trailing_slash(self):
        api = zeit.push.mobile.ConnectionBase(1)
        api.config['push-target-url'] = 'http://bar.zeit.de/'
        data = api.data('', 'http://www.zeit.de/foo')
        self.assertTrue(
            data['android']['url'].startswith(
                'http://bar.zeit.de/foo'))
        self.assertTrue(
            data['ios']['url'].startswith(
                'http://bar.zeit.de/foo'))

    def test_deep_link_starts_with_app_identifier(self):
        with mock.patch('zeit.push.mobile.ConnectionBase') as ConnectionBase:
            api = ConnectionBase(1)
            api.APP_IDENTIFIER = 'foobar'
            data = api.data('', 'http://www.zeit.de/article/one')
            self.assertTrue(
                data['android']['deep_link'].startswith(
                    'foobar://article/one'))
            self.assertTrue(
                data['ios']['deep_link'].startswith(
                    'foobar://article/one'))


class StripToPathTest(unittest.TestCase):

    layer = zeit.push.testing.ZCML_LAYER

    def test_strip_to_path_works_with_full_url(self):
        self.assertEqual(
            'foo/bar?query=arg#frag',
            zeit.push.mobile.ConnectionBase.strip_to_path(
                'https://www.zeit.de/foo/bar?query=arg#frag'))

    def test_strip_to_path_works_with_partial_url(self):
        self.assertEqual(
            'foo/bar?query=arg&param',
            zeit.push.mobile.ConnectionBase.strip_to_path(
                'www.zeit.de/foo/bar?query=arg&param'))


class AddTrackingTest(unittest.TestCase):

    layer = zeit.push.testing.ZCML_LAYER

    def test_adds_tracking_information_as_query_string(self):
        url = zeit.push.mobile.ConnectionBase.add_tracking(
            'http://www.zeit.de/foo/bar', ['News'], 'android')
        qs = urlparse.parse_qs(urlparse.urlparse(url).query)
        self.assertEqual(
            'fix.int.zonaudev.push.wichtige_news.zeitde.andpush.link.x',
            qs['wt_zmc'][0])
        self.assertEqual('zeitde_andpush_link_x', qs['utm_content'][0])
        self.assertEqual('push_zonaudev_int', qs['utm_source'][0])
        self.assertEqual('wichtige_news', qs['utm_campaign'][0])
        self.assertEqual('fix', qs['utm_medium'][0])

    def test_adds_tracking_information_blog(self):
        url = zeit.push.mobile.ConnectionBase.add_tracking(
            'http://www.zeit.de/blog/foo/bar?feed=articlexml',
            ['News'], 'android')
        qs = urlparse.parse_qs(urlparse.urlparse(url).query)
        self.assertEqual('articlexml', qs['feed'][0])
        self.assertEqual('push_zonaudev_int', qs['utm_source'][0])

    def test_creates_android_push_link_for_android(self):
        url = zeit.push.mobile.ConnectionBase.add_tracking(
            'http://URL', [], 'android')
        qs = urlparse.parse_qs(urlparse.urlparse(url).query)
        self.assertEqual('zeitde_andpush_link_x', qs['utm_content'][0])

    def test_creates_ios_push_link_for_ios(self):
        url = zeit.push.mobile.ConnectionBase.add_tracking(
            'http://URL', [], 'ios')
        qs = urlparse.parse_qs(urlparse.urlparse(url).query)
        self.assertEqual('zeitde_iospush_link_x', qs['utm_content'][0])

    def test_creates_breaking_news_link_for_breaking_news_channel(self):
        url = zeit.push.mobile.ConnectionBase.add_tracking(
            'http://URL', ['Eilmeldung'], 'device')
        qs = urlparse.parse_qs(urlparse.urlparse(url).query)
        self.assertEqual('eilmeldung', qs['utm_campaign'][0])

    def test_creates_news_link_for_news_channel(self):
        url = zeit.push.mobile.ConnectionBase.add_tracking(
            'http://URL', ['News'], 'device')
        qs = urlparse.parse_qs(urlparse.urlparse(url).query)
        self.assertEqual('wichtige_news', qs['utm_campaign'][0])


class MessageTest(zeit.push.testing.TestCase):

    name = 'mobile'

    def create_content(self, image=None, **kw):
        """Create content with values given in arguments."""
        from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
        content = ExampleContentType()
        for key, value in kw.items():
            setattr(content, key, value)
        if image is not None:
            zeit.content.image.interfaces.IImages(content).image = image
        self.repository['content'] = content
        return self.repository['content']

    def get_calls(self, service_name):
        push_notifier = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name=service_name)
        return push_notifier.calls

    def test_sends_push_via_urbanairship(self):
        message = zope.component.getAdapter(
            self.create_content(title='content_title'),
            zeit.push.interfaces.IMessage, name=self.name)
        message.send()
        self.assertEqual(1, len(self.get_calls('urbanairship')))

    def test_provides_image_url_if_image_is_referenced(self):
        from zeit.cms.interfaces import ICMSContent
        image = ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        message = zope.component.getAdapter(
            self.create_content(image=image),
            zeit.push.interfaces.IMessage, name=self.name)
        self.assertEqual(image, message.image)
        self.assertEqual(
            'http://img.zeit.de/2006/DSC00109_2.JPG',
            message.additional_parameters['image_url'])

    def test_reads_metadata_from_content(self):
        message = zope.component.getAdapter(
            self.create_content(title='content_title', teaserTitle='title',
                                teaserSupertitle='super', teaserText='teaser'),
            zeit.push.interfaces.IMessage, name=self.name)
        message.send()
        self.assertEqual(
            [('content_title', u'http://www.zeit.de/content', {
                'teaserSupertitle': 'super', 'teaserText': 'teaser',
                'teaserTitle': 'title'})],
            self.get_calls('urbanairship'))

    def test_message_text_favours_override_text_over_title(self):
        message = zope.component.getAdapter(
            self.create_content(title='nay'),
            zeit.push.interfaces.IMessage, name=self.name)
        message.config = {'override_text': 'yay'}
        message.send()
        self.assertEqual('yay', message.text)
        self.assertEqual('yay', self.get_calls('urbanairship')[0][0])


class PushNewsFlagTest(zeit.push.testing.TestCase):

    def test_sets_flag_on_checkin(self):
        content = self.repository['testcontent']
        self.assertFalse(content.push_news)
        with checked_out(content) as co:
            push = zeit.push.interfaces.IPushMessages(co)
            push.message_config = ({
                'type': 'mobile', 'enabled': True,
                'channels': CONFIG_CHANNEL_NEWS,
            },)
        content = self.repository['testcontent']
        self.assertTrue(content.push_news)


class IntegrationTest(zeit.push.testing.TestCase):

    def setUp(self):
        from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
        super(IntegrationTest, self).setUp()
        content = ExampleContentType()
        content.title = 'content_title'
        self.repository['content'] = content
        self.content = self.repository['content']

    def publish(self, content):
        from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
        IPublishInfo(content).urgent = True
        IPublish(content).publish()
        zeit.workflow.testing.run_publish()

    def test_publish_triggers_push_notification_via_message_config(self):
        from zeit.push.interfaces import IPushMessages
        push = IPushMessages(self.content)
        push.message_config = [{'type': 'mobile', 'enabled': True}]
        self.publish(self.content)
        self.assertEqual([(
            'content_title', u'http://www.zeit.de/content',
            {'enabled': True, 'type': 'mobile'})],
            zope.component.getUtility(
                zeit.push.interfaces.IPushNotifier, name='urbanairship').calls)
