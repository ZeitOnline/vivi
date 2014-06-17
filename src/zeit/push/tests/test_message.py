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

    def test_short_text_is_truncated_with_ellipsis(self):
        content = self.repository['testcontent']
        push = zeit.push.interfaces.IPushMessages(content)
        push.short_text = 'a' * 106 + ' This is too long'
        message = zope.component.getAdapter(
            content, zeit.push.interfaces.IMessage, name='parse')
        self.assertEqual(117, len(message.text))
        self.assertTrue(message.text.endswith('This is...'))

    def test_short_text_is_left_alone_if_below_limit(self):
        content = self.repository['testcontent']
        push = zeit.push.interfaces.IPushMessages(content)
        push.short_text = 'a' * 100 + ' This is not long'
        message = zope.component.getAdapter(
            content, zeit.push.interfaces.IMessage, name='parse')
        self.assertEqual(push.short_text, message.text)

    def test_long_text_is_left_alone(self):
        content = self.repository['testcontent']
        push = zeit.push.interfaces.IPushMessages(content)
        push.long_text = 'a' * 200
        message = zope.component.getAdapter(
            content, zeit.push.interfaces.IMessage, name='facebook')
        self.assertEqual(push.long_text, message.text)
