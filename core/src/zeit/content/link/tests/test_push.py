import zope.component

import zeit.content.link.link
import zeit.content.link.testing
import zeit.push.interfaces


class PushURLTest(zeit.content.link.testing.FunctionalTestCase):
    def test_push_uses_url_of_target_instead_of_link_object(self):
        link = zeit.content.link.link.Link()
        link.url = 'http://example.com/'
        message = zope.component.getAdapter(link, zeit.push.interfaces.IMessage, name='mobile')
        self.assertEqual('http://example.com/', message.url)
