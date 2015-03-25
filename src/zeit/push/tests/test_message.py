from zeit.cms.testcontenttype.testcontenttype import TestContentType
import zeit.push.interfaces
import zeit.push.testing
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

    def test_parse_reads_supertitle_from_content(self):
        content = TestContentType()
        content.title = 'mytext'
        content.supertitle = 'super'
        self.repository['foo'] = content
        message = zope.component.getAdapter(
            content, zeit.push.interfaces.IMessage, name='parse')
        message.send()
        parse = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name='parse')
        self.assertEqual(
            [('mytext', u'http://www.zeit.de/foo', {'supertitle': 'super'})],
            parse.calls)
