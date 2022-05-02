from unittest import mock
from zeit.cms.interfaces import ICMSContent
import zeit.push.grafana
import zeit.push.testing
import zeit.push.urbanairship


class ConnectionTest(zeit.push.testing.TestCase):

    def test_posts_data_as_json(self):
        api = zeit.push.grafana.Connection('', '')
        message = zeit.push.urbanairship.Message(
            ICMSContent("http://xml.zeit.de/online/2007/01/Somalia"))
        message.config = {
            'payload_template': 'template.json',
            'override_text': 'foo',
            'type': 'mobile'
        }
        with mock.patch('requests.post') as post:
            api.send(message.text, message.url, **message.config)
            self.assertEqual({
                'tags': ['push', 'www', 'template'],
                'text': 'http://www.zeit.de/online/2007/01/Somalia'
            }, post.call_args[1]['json'])
