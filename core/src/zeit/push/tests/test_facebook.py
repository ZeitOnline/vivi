# coding: utf-8
import zope.component

from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.push.interfaces
import zeit.push.testing


class FacebookMessageTest(zeit.push.testing.TestCase):
    def test_uses_facebook_override_text(self):
        content = ExampleContentType()
        self.repository['foo'] = content
        push = zeit.push.interfaces.IPushMessages(content)
        push.message_config = [
            {'type': 'facebook', 'enabled': True, 'account': 'fb-test', 'override_text': 'facebook'}
        ]
        message = zope.component.getAdapter(content, zeit.push.interfaces.IMessage, name='facebook')
        # XXX This API is a bit unwieldy
        # (see zeit.push.workflow.PushMessages._create_message)
        message.config = push.message_config[0]
        self.assertEqual('facebook', message.text)

    def test_adds_campaign_parameters_to_url(self):
        content = self.repository['testcontent']
        message = zope.component.getAdapter(content, zeit.push.interfaces.IMessage, name='facebook')
        self.assertIn('wt_zmc=sm.int.zonaudev.facebook', message.url)
