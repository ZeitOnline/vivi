from datetime import datetime
from zeit.cms.checkout.helper import checked_out
from zeit.push.interfaces import PARSE_NEWS_CHANNEL
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
        catalog.messages['parse-news-title'] = 'bar'
        catalog.messages['parse-breaking-title'] = 'foo'
        api = zeit.push.mobile.ConnectionBase(1)
        api.LANGUAGE = 'tt'
        self.assertEqual('bar', api.get_headline(['News']))
        self.assertEqual('foo', api.get_headline(['Eilmeldung']))

    def test_transmits_metadata(self):
        catalog = self.create_catalog()
        catalog.messages['parse-news-title'] = 'ZEIT ONLINE'
        api = zeit.push.mobile.ConnectionBase(1)
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
        api = zeit.push.mobile.ConnectionBase(1)
        data = api.data('foo', 'any', override_text='mytext')
        self.assertEqual('mytext', data['android']['text'])
        self.assertEqual('mytext', data['ios']['alert'])


class RewriteURLTest(unittest.TestCase):

    target_host = 'http://www.staging.zeit.de/'

    def rewrite(self, url):
        return zeit.push.mobile.ConnectionBase.rewrite_url(
            url, self.target_host)

    def test_www_zeit_de_is_replaced_with_staging(self):
        self.assertEqual(
            self.target_host + 'foo/bar',
            self.rewrite('http://www.zeit.de/foo/bar'))

    def test_blog_zeit_de_is_replaced_with_staging_and_appends_query(self):
        self.assertEqual(
            self.target_host + 'blog/foo/bar?feed=articlexml',
            self.rewrite('http://blog.zeit.de/foo/bar'))

    def test_zeit_de_blog_is_replaced_with_staging_and_appends_query(self):
        self.assertEqual(
            self.target_host + 'blog/foo/bar?feed=articlexml',
            self.rewrite('http://www.zeit.de/blog/foo/bar'))


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

    def test_sends_push_via_parse_and_urbanairship(self):
        message = zope.component.getAdapter(
            self.create_content(title='content_title'),
            zeit.push.interfaces.IMessage, name=self.name)
        message.send()
        self.assertEqual(1, len(self.get_calls('parse')))
        self.assertEqual(1, len(self.get_calls('urbanairship')))

    def test_sends_push_to_parse_if_urbanairship_fails(self):
        from zeit.push.interfaces import WebServiceError
        message = zope.component.getAdapter(
            self.create_content(title='content_title'),
            zeit.push.interfaces.IMessage, name=self.name)
        urbanairship_notifier = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name='urbanairship')
        with mock.patch.object(urbanairship_notifier, 'send',
                               side_effect=WebServiceError('Unauthorized')):
            message.send()
            self.assertEqual(1, len(self.get_calls('parse')))
            self.assertEqual(0, len(self.get_calls('urbanairship')))

    def test_sends_push_to_urbanairship_if_parse_fails(self):
        from zeit.push.interfaces import WebServiceError
        message = zope.component.getAdapter(
            self.create_content(title='content_title'),
            zeit.push.interfaces.IMessage, name=self.name)
        parse_notifier = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name='parse')
        with mock.patch.object(parse_notifier, 'send',
                               side_effect=WebServiceError('Unauthorized')):
            message.send()
            self.assertEqual(0, len(self.get_calls('parse')))
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
            self.get_calls('parse'))
        self.assertEqual(
            [('content_title', u'http://www.zeit.de/content', {
                'teaserSupertitle': 'super', 'teaserText': 'teaser',
                'teaserTitle': 'title'})],
            self.get_calls('urbanairship'))


class ParseMessageTest(zeit.push.testing.TestCase):
    """Ensure bw-compat for messages retrieved for `parse` message configs."""

    name = 'parse'


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
                zeit.push.interfaces.IPushNotifier, name='parse').calls)
        self.assertEqual([(
            'content_title', u'http://www.zeit.de/content',
            {'enabled': True, 'type': 'mobile'})],
            zope.component.getUtility(
                zeit.push.interfaces.IPushNotifier, name='urbanairship').calls)
