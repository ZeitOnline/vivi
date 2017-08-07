# coding=utf-8
from datetime import datetime
from zeit.cms.interfaces import ICMSContent
import json
import mock
import os
import pytz
import gocept.testing.assertion
import urbanairship.push.core
import zeit.push.interfaces
import zeit.push.testing
import zeit.push.urbanairship
import zope.component


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
            None, None, None, None, None, None, 1)
        self.message = zeit.push.urbanairship.Message(
            ICMSContent("http://xml.zeit.de/online/2007/01/Somalia"))
        self.message.config = {
            'uses_image': True,
            'payload_template': u'template.json',
            'enabled': True,
            'override_text': u'foo',
            'type': 'mobile'
        }
        self.create_payload_template()

    def test_sets_expiration_time_in_payload(self):
        self.api.expire_interval = 3600
        with mock.patch('zeit.push.urbanairship.datetime') as mock_datetime:
            mock_datetime.now.return_value = (
                datetime(2014, 07, 1, 10, 15, 7, 38, tzinfo=pytz.UTC))
            with mock.patch.object(self.api, 'push') as push:
                self.api.send('any', 'any', message=self.message)
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


class PayloadSourceTest(zeit.push.testing.TestCase):

    def setUp(self):
        super(PayloadSourceTest, self).setUp()
        self.create_payload_template()
        self.templates = list(zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE)

    def test_getValues_returns_all_templates_as_text_objects(self):
        # Change this if we decide we want a new
        # content type PaylaodTemplate
        self.assertTrue(1, len(self.templates))
        self.assertTrue(zeit.content.text.text.Text, type(self.templates[0]))

    def test_getTitle_returns_capitalized_title(self):
        self.assertTrue('Template',
                        zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE.factory
                        .getTitle(self.templates[0]))

    def test_getToken_returns_template_name(self):
        self.assertTrue('template.json',
                        zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE.factory
                        .getToken(self.templates[0]))

    def test_find_returns_correct_template(self):
        template_name = 'template.json'
        result = zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE.factory.find(
            template_name)
        self.assertEqual(template_name, result.__name__)


class MessageTest(zeit.push.testing.TestCase,
                  gocept.testing.assertion.String):

    name = 'mobile'

    def create_content(self, **kw):
        """Create content with values given in arguments."""
        from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
        content = ExampleContentType()
        for key, value in kw.items():
            setattr(content, key, value)
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
        message = zope.component.getAdapter(
            self.create_content(),
            zeit.push.interfaces.IMessage, name=self.name)
        message.config['image'] = 'http://xml.zeit.de/2006/DSC00109_2.JPG'
        self.assertEqual(
            'http://img.zeit.de/2006/DSC00109_2.JPG', message.image_url)

    def test_reads_metadata_from_content(self):
        message = zope.component.getAdapter(
            self.create_content(title='content_title', teaserTitle='title',
                                teaserSupertitle='super', teaserText='teaser'),
            zeit.push.interfaces.IMessage, name=self.name)
        message.send()
        self.assertEqual(
            [('content_title', u'http://www.zeit.de/content',
              {'message': message})],
            self.get_calls('urbanairship'))

    def test_message_text_favours_override_text_over_title(self):
        message = zope.component.getAdapter(
            self.create_content(title='nay'),
            zeit.push.interfaces.IMessage, name=self.name)
        message.config = {'override_text': 'yay'}
        message.send()
        self.assertEqual('yay', message.text)
        self.assertEqual('yay', self.get_calls('urbanairship')[0][0])

    def test_changes_to_template_are_applied_immediately(self):
        message = zeit.push.urbanairship.Message(
            self.repository['testcontent'])
        self.create_payload_template('{"messages": {"one": 1}}', 'foo.json')
        message.config['payload_template'] = 'foo.json'
        self.assertEqual({'one': 1}, message.render())
        self.create_payload_template('{"messages": {"two": 1}}', 'foo.json')
        self.assertEqual({'two': 1}, message.render())

    def test_payload_loads_jinja_payload_variables(self):
        template_content = u"""{"messages":[{
            "title": "{{article.title}}",
            "message": "{%if not uses_image %}Bildß{% endif %}"
        }]}"""
        self.create_payload_template(template_content, 'bar.json')
        message = zope.component.getAdapter(
            self.create_content(),
            zeit.push.interfaces.IMessage, name=self.name)
        message.config['payload_template'] = 'bar.json'
        payload = message.render()
        self.assertEqual(u'Bildß', payload[0].get('message'))
        self.assertEqual(message.context.title, payload[0].get('title'))

    def test_deep_link_starts_with_app_identifier(self):
        message = zope.component.getAdapter(
            self.create_content(),
            zeit.push.interfaces.IMessage, name=self.name)
        self.assertStartsWith(message.app_link, 'zeitapp://content')

    def test_template_escapes_variables_for_json(self):
        template_content = u"""{"messages":[{
            "title": "{{article.title}}"
            "subtitle": "{{foo}}"
        }]}"""
        self.create_payload_template(template_content, 'bar.json')
        message = zope.component.getAdapter(
            self.create_content(title='"Quoted" Title'),
            zeit.push.interfaces.IMessage, name=self.name)
        message.config['payload_template'] = 'bar.json'
        message.config['foo'] = 'with "quotes"'
        payload = message.render()
        self.assertEqual('"Quoted" Title', payload['title'])
        self.assertEqual('with "quotes"', payload['subtitle'])


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
        calls = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name='urbanairship').calls
        self.assertEqual(calls[0][0], 'content_title')
        self.assertEqual(calls[0][1], u'http://www.zeit.de/content')
        self.assertEqual(calls[0][2].get('enabled'), True)
        self.assertEqual(calls[0][2].get('type'), 'mobile')


class PushTest(zeit.push.testing.TestCase):

    level = 2

    def setUp(self):
        super(PushTest, self).setUp()
        self.message = zeit.push.urbanairship.Message(
            self.repository['testcontent'])
        self.message.config['payload_template'] = 'foo.json'
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

    def test_push_works(self):
        with mock.patch('urbanairship.push.core.Push.send', send):
            with mock.patch('urbanairship.push.core.PushResponse') as push:
                self.api.send('any', 'any', message=self.message)
                self.assertEqual(200, push.call_args[0][0].status_code)

    def test_invalid_credentials_should_raise(self):
        invalid_connection = zeit.push.urbanairship.Connection(
            'invalid', 'invalid', 'invalid', 'invalid', 'invalid', 'invalid',
            1)
        with self.assertRaises(zeit.push.interfaces.WebServiceError):
            invalid_connection.send('any', 'any', message=self.message)

    def test_server_error_should_raise(self):
        response = mock.Mock()
        response.status_code = 500
        response.headers = {}
        response.content = ''
        response.json.return_value = {}
        with mock.patch('requests.sessions.Session.request') as request:
            request.return_value = response
            with self.assertRaises(zeit.push.interfaces.TechnicalError):
                self.api.send('any', 'any', message=self.message)
