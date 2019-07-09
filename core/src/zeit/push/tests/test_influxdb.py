from zeit.cms.interfaces import ICMSContent
import mock
import zeit.push.influxdb
import zeit.push.testing
import zeit.push.urbanairship


class ConnectionTest(zeit.push.testing.TestCase):

    def test_posts_data_as_json(self):
        api = zeit.push.influxdb.Connection(
            None, None, None, None, None)
        message = zeit.push.urbanairship.Message(
            ICMSContent("http://xml.zeit.de/online/2007/01/Somalia"))
        message.config = {
            'payload_template': u'template.json',
            'override_text': u'foo',
            'type': 'mobile'
        }
        with mock.patch('requests.post') as post:
            api.send(message.text, message.url, **message.config)
            self.assertEqual([
                'Push', 'push,www,template',
                'http://www.zeit.de/online/2007/01/Somalia'
            ], post.call_args[1]['json'][0]['points'][0])
