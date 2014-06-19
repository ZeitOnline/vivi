import zeit.push.interfaces
import zeit.push.testing
import zope.component


class MessageTest(zeit.push.testing.TestCase):

    def test_send_delegates_to_IPushNotifier_utility(self):
        content = self.repository['testcontent']
        push = zeit.push.interfaces.IPushMessages(content)
        push.short_text = 'mytext'
        message = zope.component.getAdapter(
            content, zeit.push.interfaces.IMessage, name='parse')
        message.send()
        parse = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name='parse')
        self.assertEqual(
            [('mytext', u'http://www.zeit.de/testcontent', {})], parse.calls)
