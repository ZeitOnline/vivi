import json
import mock
import unittest
import urbanairship.push.core
import zeit.push.urbanairship


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


class UrbanAirshipTest(unittest.TestCase):

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
