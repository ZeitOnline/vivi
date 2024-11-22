# coding=utf-8
from datetime import datetime
from unittest import mock
import os
import unittest

import pytest
import requests_mock
import time_machine
import zope.component
import zope.event

from zeit.cms.interfaces import ICMSContent
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.cms.workflow.interfaces import IPublish
import zeit.cms.checkout.helper
import zeit.cms.content.interfaces
import zeit.push.interfaces
import zeit.push.testing
import zeit.push.urbanairship


class ConnectionTest(zeit.push.testing.TestCase):
    def setUp(self):
        super().setUp()
        self.api = zeit.push.urbanairship.Connection(None, None, None, expire_interval=3600)
        self.message = zeit.push.urbanairship.Message(
            ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        )
        self.message.config = {
            'uses_image': True,
            'payload_template': 'template.json',
            'enabled': True,
            'override_text': 'foo',
            'type': 'mobile',
        }
        self.create_payload_template()

    @time_machine.travel(datetime(2014, 7, 1, 10, 15, 7, 38))
    def test_template_content_is_transformed_to_ua_payload(self):
        with mock.patch.object(self.api, 'push') as push:
            self.api.send('any', 'any', message=self.message)
            android = push.call_args[0][0][0]
            self.assertEqual(['android'], android['device_types'])
            self.assertEqual(
                # Given in template
                '2014-07-01T10:45:07',
                android['options']['expiry'],
            )
            self.assertEqual(
                {'group': 'subscriptions', 'tag': 'Eilmeldung'}, android['audience']['OR'][0]
            )
            self.assertEqual('foo', android['notification']['alert'])
            self.assertEqual(
                'Rückkehr der Warlords', android['notification']['android']['extra']['headline']
            )
            self.assertEqual(
                '4850d936-a3b7-4ff0-8434-57d26ca7521b',
                android['notification']['android']['uuid'],
            )

            ios = push.call_args[0][0][1]
            self.assertEqual(['ios'], ios['device_types'])
            self.assertEqual(
                # Defaults to configured expiration_interval
                '2014-07-01T11:15:07',
                ios['options']['expiry'],
            )
            self.assertEqual(
                {'group': 'subscriptions', 'tag': 'Eilmeldung'}, ios['audience']['OR'][0]
            )
            self.assertEqual('foo', ios['notification']['alert'])
            self.assertEqual('Rückkehr der Warlords', ios['notification']['ios']['title'])
            self.assertEqual(
                '4850d936-a3b7-4ff0-8434-57d26ca7521b', ios['notification']['ios']['uuid']
            )

            open_slack = push.call_args[0][0][2]
            self.assertEqual(['open::slack'], open_slack['device_types'])
            self.assertEqual('2014-07-01T11:15:07', open_slack['options']['expiry'])
            self.assertEqual(
                {'open_channel': 'cec48c28-4486-4c95-989e-0bbed3edc714'}, open_slack['audience']
            )
            self.assertEqual('foo', open_slack['notification']['alert'])
            self.assertEqual(
                'Nicht Corona', open_slack['notification']['open::slack']['extra']['recipients']
            )


class PayloadSourceTest(zeit.push.testing.TestCase):
    def setUp(self):
        super().setUp()
        self.create_payload_template()
        self.templates = list(zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE)

    def test_getValues_returns_all_templates_as_text_objects(self):
        # Change this if we decide we want a new
        # content type PaylaodTemplate
        self.assertTrue(1, len(self.templates))
        self.assertTrue(zeit.content.text.text.Text, type(self.templates[0]))

    def test_getTitle_returns_capitalized_title(self):
        self.assertTrue(
            'Template',
            zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE.factory.getTitle(self.templates[0]),
        )

    def test_getToken_returns_template_name(self):
        self.assertTrue(
            'template.json',
            zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE.factory.getToken(self.templates[0]),
        )

    def test_find_returns_correct_template(self):
        template_name = 'template.json'
        result = zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE.factory.find(template_name)
        self.assertEqual(template_name, result.__name__)


class MessageTest(zeit.push.testing.TestCase):
    name = 'mobile'

    def create_content(self, with_authors=False, **kw):
        """Create content with values given in arguments."""
        content = ExampleContentType()
        for key, value in kw.items():
            setattr(content, key, value)
        if with_authors:
            shakespeare = zeit.content.author.author.Author()
            shakespeare.firstname = 'William'
            shakespeare.lastname = 'Shakespeare'
            shakespeare.enable_followpush = True
            bacon = zeit.content.author.author.Author()
            bacon.firstname = 'Francis'
            bacon.lastname = 'Bacon'
            self.repository['shakespeare'] = shakespeare
            self.repository['bacon'] = bacon
            shakespeare.enable_followpush = False
            content.authorships = [
                content.authorships.create(self.repository['shakespeare']),
                content.authorships.create(self.repository['bacon']),
            ]
        self.repository['content'] = content
        return self.repository['content']

    def get_calls(self, service_name):
        push_notifier = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name=service_name
        )
        return push_notifier.calls

    def test_sends_push_via_urbanairship(self):
        message = zope.component.getAdapter(
            self.create_content(title='content_title'),
            zeit.push.interfaces.IMessage,
            name=self.name,
        )
        message.send()
        self.assertEqual(1, len(self.get_calls('urbanairship')))

    def test_provides_image_url_if_image_is_referenced(self):
        message = zope.component.getAdapter(
            self.create_content(), zeit.push.interfaces.IMessage, name=self.name
        )
        message.config['image'] = 'http://xml.zeit.de/2006/DSC00109_2.JPG'
        self.assertEqual('http://img.zeit.de/2006/DSC00109_2.JPG', message.image_url)

    def test_reads_metadata_from_content(self):
        message = zope.component.getAdapter(
            self.create_content(
                title='content_title',
                teaserTitle='title',
                teaserSupertitle='super',
                teaserText='teaser',
            ),
            zeit.push.interfaces.IMessage,
            name=self.name,
        )
        message.send()
        self.assertEqual(
            [('content_title', 'http://www.zeit.de/content', {'message': message})],
            self.get_calls('urbanairship'),
        )

    def test_message_text_favours_override_text_over_title(self):
        message = zope.component.getAdapter(
            self.create_content(title='nay'), zeit.push.interfaces.IMessage, name=self.name
        )
        message.config = {'override_text': 'yay'}
        message.send()
        self.assertEqual('yay', message.text)
        self.assertEqual('yay', self.get_calls('urbanairship')[0][0])

    def test_changes_to_template_are_applied_immediately(self):
        message = zeit.push.urbanairship.Message(self.repository['testcontent'])
        self.create_payload_template('{"messages": {"one": 1}}', 'foo.json')
        message.config['payload_template'] = 'foo.json'
        self.assertEqual({'one': 1}, message.render())
        self.create_payload_template('{"messages": {"two": 1}}', 'foo.json')
        self.assertEqual({'two': 1}, message.render())

    def test_payload_loads_jinja_payload_variables(self):
        template_content = """{"messages":[{
            "title": "{{article.title}}",
            "message": "{%if not uses_image %}Bildß{% endif %}"
        }]}"""
        self.create_payload_template(template_content, 'bar.json')
        message = zope.component.getAdapter(
            self.create_content(), zeit.push.interfaces.IMessage, name=self.name
        )
        message.config['payload_template'] = 'bar.json'
        payload = message.render()
        self.assertEqual('Bildß', payload[0].get('message'))
        self.assertEqual(message.context.title, payload[0].get('title'))

    def test_deep_link_starts_with_app_identifier(self):
        message = zope.component.getAdapter(
            self.create_content(), zeit.push.interfaces.IMessage, name=self.name
        )
        self.assertStartsWith(message.app_link, 'zeitapp://content')


class IntegrationTest(zeit.push.testing.TestCase):
    def setUp(self):
        super().setUp()
        content = ExampleContentType()
        content.title = 'content_title'
        self.repository['content'] = content
        self.content = self.repository['content']

    def test_publish_triggers_push_notification_via_message_config(self):
        from zeit.push.interfaces import IPushMessages

        push = IPushMessages(self.content)
        push.message_config = [{'type': 'mobile', 'enabled': True}]
        IPublish(self.content).publish()
        calls = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name='urbanairship'
        ).calls
        self.assertEqual(calls[0][0], 'content_title')
        self.assertEqual(calls[0][1], 'http://www.zeit.de/content')
        self.assertEqual(calls[0][2].get('enabled'), True)
        self.assertEqual(calls[0][2].get('type'), 'mobile')


@pytest.mark.integration()
class PushTest(zeit.push.testing.TestCase):
    level = 2

    def setUp(self):
        super().setUp()
        self.message = zeit.push.urbanairship.Message(self.repository['testcontent'])
        self.message.config['payload_template'] = 'foo.json'
        self.api = zeit.push.urbanairship.Connection(
            os.environ['ZEIT_PUSH_URBANAIRSHIP_BASE_URL'],
            os.environ['ZEIT_PUSH_URBANAIRSHIP_APPLICATION_KEY'],
            os.environ['ZEIT_PUSH_URBANAIRSHIP_MASTER_SECRET'],
            expire_interval=1,
        )

    @unittest.skip('UA has too tight validation, nonsense requests fail')
    def test_push_works(self):
        self.api.ENDPOINT = '/push/validate'
        with self.assertNothingRaised():
            self.api.send('any', 'any', message=self.message)

    def test_invalid_credentials_should_raise(self):
        invalid_connection = zeit.push.urbanairship.Connection(
            os.environ['ZEIT_PUSH_URBANAIRSHIP_BASE_URL'], 'invalid', 'invalid', expire_interval=1
        )
        with self.assertRaises(zeit.push.interfaces.WebServiceError):
            invalid_connection.send('any', 'any', message=self.message)

    def test_server_error_should_raise(self):
        http = requests_mock.Mocker()
        http.post(
            os.environ['ZEIT_PUSH_URBANAIRSHIP_BASE_URL'] + self.api.ENDPOINT, status_code=500
        )
        with http:
            with self.assertRaises(zeit.push.interfaces.TechnicalError):
                self.api.send('any', 'any', message=self.message)
