import json
import mock
import os
import unittest
import urbanairship.push.core
import zeit.push.interfaces
import zeit.push.testing
import zeit.push.urbanairship
import zeit.workflow.testing
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


class ConnectionTest(unittest.TestCase):

    level = 2

    def setUp(self):
        super(ConnectionTest, self).setUp()
        self.application_key = os.environ[
            'ZEIT_PUSH_URBANAIRSHIP_APPLICATION_KEY']
        self.master_secret = os.environ['ZEIT_PUSH_URBANAIRSHIP_MASTER_SECRET']

    def test_push_works(self):
        with mock.patch('urbanairship.push.core.Push.send', send):
            api = zeit.push.urbanairship.Connection(
                self.application_key, self.master_secret, 1)
            response = api.send('Being pushy.', 'http://example.com')
            self.assertEqual(True, response.ok)


class PushNotifierTest(zeit.push.testing.TestCase):

    def setUp(self):
        from zeit.cms.testcontenttype.testcontenttype import TestContentType
        super(PushNotifierTest, self).setUp()
        content = TestContentType()
        content.title = 'content_title'
        self.repository['content'] = content
        self.content = self.repository['content']

    def publish(self, content):
        from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
        IPublishInfo(content).urgent = True
        IPublish(content).publish()
        zeit.workflow.testing.run_publish()

    def test_send_on_message_delegates_to_IPushNotifier_utility(self):
        message = zope.component.getAdapter(
            self.content, zeit.push.interfaces.IMessage, name='urbanairship')
        message.send()

        urbanairship = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name='urbanairship')
        self.assertEqual(
            [('content_title', u'http://www.zeit.de/content', {})],
            urbanairship.calls)

    def test_publish_triggers_send_on_IPushNotifier_utility(self):
        from zeit.push.interfaces import IPushMessages
        push = IPushMessages(self.content)
        push.message_config = [{'type': 'urbanairship', 'enabled': True}]
        self.publish(self.content)

        urbanairship = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name='urbanairship')
        self.assertEqual([(
            'content_title', u'http://www.zeit.de/content',
            {'enabled': True, 'type': 'urbanairship'})],
            urbanairship.calls)
