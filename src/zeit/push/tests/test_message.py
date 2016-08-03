from zeit.cms.testcontenttype.testcontenttype import TestContentType
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
import zeit.push.interfaces
import zeit.push.testing
import zeit.workflow.testing
import zope.component


class MessageTest(zeit.push.testing.TestCase):

    def test_send_delegates_to_IPushNotifier_utility(self):
        content = TestContentType()
        content.title = 'mytext'
        self.repository['foo'] = content
        message = zope.component.getAdapter(
            content, zeit.push.interfaces.IMessage, name='parse')
        message.send()
        parse = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name='parse')
        self.assertEqual(
            [('mytext', u'http://www.zeit.de/foo', {})], parse.calls)

    def test_no_text_configured_should_not_send(self):
        content = self.repository['testcontent']
        message = zope.component.getAdapter(
            content, zeit.push.interfaces.IMessage, name='parse')
        with self.assertRaises(ValueError):
            message.send()
        parse = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name='parse')
        self.assertEqual([], parse.calls)

    def publish(self, content):
        IPublishInfo(content).urgent = True
        IPublish(content).publish()
        zeit.workflow.testing.run_publish()

    def test_enabled_flag_is_removed_from_service_after_send(self):
        content = TestContentType()
        content.title = 'mytext'
        self.repository['foo'] = content
        push = zeit.push.interfaces.IPushMessages(content)
        push.message_config = [{'type': 'parse', 'enabled': True}]
        self.publish(content)
        self.assertEqual(
            [{'type': 'parse', 'enabled': False}], push.message_config)
