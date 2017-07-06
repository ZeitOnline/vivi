from datetime import datetime
from zeit.cms.checkout.helper import checked_out
from zeit.push.interfaces import CONFIG_CHANNEL_BREAKING, CONFIG_CHANNEL_NEWS
from zeit.cms.interfaces import ICMSContent
import json
import mock
import os
import pytz
import unittest
import urlparse
import gocept.testing.assertion
import urbanairship.push.core
import zeit.cms.testing
import zeit.content.image.interfaces
import zeit.push.interfaces
import zeit.push.testing
import zeit.push.urbanairship
import zope.app.appsetup.product
import zope.component
import zope.i18n.translationdomain


def send(self):
    """Mock that sends to /validate/.

    We cannot mock the URL only, since the logger in the original `send`
    expects more data to be returned by the response.

    """
    body = json.dumps(self.payload)
    response = self._airship._request(
        method='POST',
        body=body,
        url='https://go.urbanairship.com/api/push/validate/',
        content_type='application/json',
        version=3
    )
    return urbanairship.push.core.PushResponse(response)


class ConnectionTest(zeit.push.testing.TestCase):

    def setUp(self):
        super(ConnectionTest, self).setUp()
        self.api = zeit.push.urbanairship.Connection(
            os.environ[
                'ZEIT_PUSH_URBANAIRSHIP_ANDROID_APPLICATION_KEY'],
            os.environ[
                'ZEIT_PUSH_URBANAIRSHIP_ANDROID_MASTER_SECRET'],
            os.environ[
                'ZEIT_PUSH_URBANAIRSHIP_IOS_APPLICATION_KEY'],
            os.environ[
                'ZEIT_PUSH_URBANAIRSHIP_IOS_MASTER_SECRET'],
            os.environ[
                'ZEIT_PUSH_URBANAIRSHIP_WEB_APPLICATION_KEY'],
            os.environ[
                'ZEIT_PUSH_URBANAIRSHIP_WEB_MASTER_SECRET'],
            1
        )
        self.additional_params = \
            {
                'push_config': {
                    'uses_image': False,
                    'payload_template':
                        u'http://xml.zeit.de/data/payload-templates/template.json',
                    'enabled': True,
                    'override_text': u'asd',
                    'channels': 'channel-news',
                    'type': 'mobile'},
                'context': ICMSContent(
                    "http://xml.zeit.de/online/2007/01/Somalia")
            }
        self.create_test_payload_template()

    # def test_push_works(self):
    #     with mock.patch('urbanairship.push.core.Push.send', send):
    #         with mock.patch('urbanairship.push.core.PushResponse') as push:
    #             self.api.send('Push', 'http://example.com',
    #                           **self.additional_params)
    #             self.assertEqual(200, push.call_args[0][0].status_code)

    def test_sets_expiration_time_in_payload(self):
        self.api.expire_interval = 3600
        with mock.patch('zeit.push.urbanairship.datetime') as mock_datetime:
            mock_datetime.now.return_value = (
                datetime(2014, 07, 1, 10, 15, 7, 38, tzinfo=pytz.UTC))
            with mock.patch.object(self.api, 'push') as push:
                self.api.send('foo', 'any', **self.additional_params)
                self.assertEqual(
                    '2014-07-01T11:15:07',
                    push.call_args_list[0][0][0].expiry)
                self.assertEqual(
                    '2014-07-01T11:15:07',
                    push.call_args_list[1][0][0].expiry)

    def test_calculates_expiration_datetime_based_on_expire_interval(self):
        self.api.expire_interval = 3600
        with mock.patch('zeit.push.urbanairship.datetime') as mock_datetime:
            mock_datetime.now.return_value = (
                datetime(2014, 07, 1, 10, 15, 7, 38, tzinfo=pytz.UTC))
            self.assertEqual(
                datetime(2014, 07, 1, 11, 15, 7, 0, tzinfo=pytz.UTC),
                self.api.expiration_datetime)

    def test_full_url_is_passed_through(self):
        template_vars = self.api.create_template_vars(
            '', 'https://www.zeit.de/foo/bar', '', {})
        self.assertTrue(
            template_vars.get('zon_link').startswith(
                'https://www.zeit.de/foo/bar'))

    def test_deep_link_starts_with_app_identifier(self):
        self.api.APP_IDENTIFIER = 'foobar'
        template_vars = self.api.create_template_vars(
            '', 'http://www.zeit.de/article/one', '', {})
        self.assertTrue(
            template_vars.get('app_link').startswith(
                'foobar://article/one'))


class PayloadSourceTest(zeit.push.testing.TestCase):

    def setUp(self):
        super(PayloadSourceTest, self).setUp()
        self.create_test_payload_template()
        self.templates = list(zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE)

    def test_getValues_returns_all_templates_as_text_objects(self):
        # Change this if we decide we want a new content type PaylaodTemplate
        self.assertTrue(1, len(self.templates))
        self.assertTrue(zeit.content.text.text.Text, type(self.templates[0]))

    def test_getTitle_returns_capitalized_title(self):
        self.assertTrue('Template',
            zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE.factory.getTitle(
                self.templates[0]))

    def test_getToken_returns_unique_id(self):
        self.assertTrue('http://xml.zeit.de/data/payload-templates/template'
                        '.json',
                        zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE.factory\
                        .getToken(self.templates[0]))

    def test_find_returns_correct_template(self):
        result = zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE.factory.find(
            'http://xml.zeit.de/data/payload-templates/template.json'
        )
        self.assertEqual(self.templates[0], result)

    def test_load_template_returns_unicode(self):
        zeit.push.urbanairship.load_template(
            'http://xml.zeit.de/data/payload-templates/template.json')


class AddTrackingTest(unittest.TestCase,
                      gocept.testing.assertion.String):

    layer = zeit.push.testing.ZCML_LAYER

    def test_adds_tracking_information_as_query_string(self):
        url = zeit.push.urbanairship.Connection.add_tracking(
            'http://www.zeit.de/foo/bar', ['News'], 'android')
        # No thanks to parse_qs() for "benevolently" ignoring this.
        self.assertNotIn('?&', url)
        qs = urlparse.parse_qs(urlparse.urlparse(url).query)
        self.assertEqual(
            'fix.int.zonaudev.push.wichtige_news.zeitde.andpush.link.x',
            qs['wt_zmc'][0])
        self.assertEqual('zeitde_andpush_link_x', qs['utm_content'][0])
        self.assertEqual('push_zonaudev_int', qs['utm_source'][0])
        self.assertEqual('wichtige_news', qs['utm_campaign'][0])
        self.assertEqual('fix', qs['utm_medium'][0])

    def test_preserves_existing_query_string(self):
        url = zeit.push.urbanairship.Connection.add_tracking(
            'http://www.zeit.de/foo/bar?baz=qux', ['News'], 'android')
        self.assertStartsWith('http://www.zeit.de/foo/bar?baz=qux&', url)
        qs = urlparse.parse_qs(urlparse.urlparse(url).query)
        self.assertEqual('qux', qs['baz'][0])

    def test_adds_tracking_information_blog(self):
        url = zeit.push.urbanairship.Connection.add_tracking(
            'http://www.zeit.de/blog/foo/bar?feed=articlexml',
            ['News'], 'android')
        qs = urlparse.parse_qs(urlparse.urlparse(url).query)
        self.assertEqual('articlexml', qs['feed'][0])
        self.assertEqual('push_zonaudev_int', qs['utm_source'][0])

    def test_creates_android_push_link_for_android(self):
        url = zeit.push.urbanairship.Connection.add_tracking(
            'http://URL', [], 'android')
        qs = urlparse.parse_qs(urlparse.urlparse(url).query)
        self.assertEqual('zeitde_andpush_link_x', qs['utm_content'][0])

    def test_creates_ios_push_link_for_ios(self):
        url = zeit.push.urbanairship.Connection.add_tracking(
            'http://URL', [], 'ios')
        qs = urlparse.parse_qs(urlparse.urlparse(url).query)
        self.assertEqual('zeitde_iospush_link_x', qs['utm_content'][0])

    def test_creates_breaking_news_link_for_breaking_news_channel(self):
        url = zeit.push.urbanairship.Connection.add_tracking(
            'http://URL', ['Eilmeldung'], 'device')
        qs = urlparse.parse_qs(urlparse.urlparse(url).query)
        self.assertEqual('eilmeldung', qs['utm_campaign'][0])

    def test_creates_news_link_for_news_channel(self):
        url = zeit.push.urbanairship.Connection.add_tracking(
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
            [('content_title', u'http://www.zeit.de/content',
              {'mobile_title': None,
               'push_config': {},
               'context': self.repository['content']})],
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
        # TODO Channels is not passed correctly anymore
        # Another way is needed
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
            {'enabled': True,
             'type': 'mobile',
             'mobile_title': None,
             'context': ICMSContent('http://xml.zeit.de/content'),
             'push_config': {'enabled': True, 'type': 'mobile'}
             })],
            zope.component.getUtility(
                zeit.push.interfaces.IPushNotifier, name='urbanairship').calls)


class PushTest(ConnectionTest):

    level = 2
    layer = zeit.push.testing.ZCML_LAYER

    def setUp(self):
        super(PushTest, self).setUp()
        self.android_application_key = os.environ[
            'ZEIT_PUSH_URBANAIRSHIP_ANDROID_APPLICATION_KEY']
        self.android_master_secret = os.environ[
            'ZEIT_PUSH_URBANAIRSHIP_ANDROID_MASTER_SECRET']
        self.ios_application_key = os.environ[
            'ZEIT_PUSH_URBANAIRSHIP_IOS_APPLICATION_KEY']
        self.ios_master_secret = os.environ[
            'ZEIT_PUSH_URBANAIRSHIP_IOS_MASTER_SECRET']
        self.web_application_key  = os.environ[
            'ZEIT_PUSH_URBANAIRSHIP_WEB_APPLICATION_KEY']
        self.web_master_secret = os.environ[
            'ZEIT_PUSH_URBANAIRSHIP_WEB_MASTER_SECRET']

    def test_push_works(self):
        api = zeit.push.urbanairship.Connection(
            self.android_application_key, self.android_master_secret,
            self.ios_application_key, self.ios_master_secret,
            self.web_application_key, self.web_master_secret, 1)
        with mock.patch('urbanairship.push.core.Push.send', send):
            with mock.patch('urbanairship.push.core.PuhResponse') as push:
                api.send('Push', 'http://example.com',
                         **self.additional_params)
                self.assertEqual(200, push.call_args[0][0].status_code)

    def test_invalid_credentials_should_raise(self):
        api = zeit.push.urbanairship.Connection(
            'invalid', 'invalid', 'invalid', 'invalid', 'invalid', 'invalid',
            1)
        with self.assertRaises(zeit.push.interfaces.WebServiceError):
            api.send('Being pushy.', 'http://example.com',
                     **self.additional_params)

    def test_server_error_should_raise(self):
        response = mock.Mock()
        response.status_code = 500
        response.headers = {}
        response.content = ''
        response.json.return_value = {}
        api = zeit.push.urbanairship.Connection(
            self.android_application_key, self.android_master_secret,
            self.ios_application_key, self.ios_master_secret,
            self.web_application_key, self.web_master_secret, 1)
        with mock.patch('requests.sessions.Session.request') as request:
            request.return_value = response
            with self.assertRaises(zeit.push.interfaces.TechnicalError):
                api.send('Being pushy.', 'http://example.com',
                         **self.additional_params)
