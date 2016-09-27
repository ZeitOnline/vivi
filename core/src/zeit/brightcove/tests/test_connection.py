# coding: utf-8
from StringIO import StringIO
import json
import mock
import unittest
import zeit.brightcove.connection


class ConnectionTest(unittest.TestCase):
    # mix in some non-ASCII chars everywhere to guard against #10600

    def test_strings_should_be_read_from_json_as_unicode(self):
        conn = zeit.brightcove.connection.APIConnection(
            None, None, None, None, None)
        response = conn.parse_json(u'{"föö": "bar"}'.encode('utf-8'))
        self.assertTrue(isinstance(response.iterkeys().next(), unicode))
        self.assertTrue(isinstance(response.itervalues().next(), unicode))

    def test_json_invalid_characters_are_removed_from_json_data(self):
        conn = zeit.brightcove.connection.APIConnection(
            None, None, None, None, None)
        response = conn.parse_json(u'{"föö": "\u0009"}'.encode('utf-8'))
        self.assertEqual('', response[u'föö'])

        response = conn.parse_json(u'{"föö": "\u2028"}'.encode('utf-8'))
        self.assertEqual('', response[u'föö'])

    def test_xml_restricted_characters_are_removed_from_json_data(self):
        conn = zeit.brightcove.connection.APIConnection(
            None, None, None, None, None)
        response = conn.parse_json(u'{"föö": "\u007f"}'.encode('utf-8'))
        self.assertEqual('', response[u'föö'])

    def test_post_writes_to_the_configured_url(self):
        conn = zeit.brightcove.connection.APIConnection(
            None, 'my-write-token', None, 'http://write.url', 4711.0)
        with mock.patch('urllib2.urlopen') as urlopen:
            urlopen.return_value = StringIO(json.dumps({'result': 'okay'}))
            result = conn.post('my-command', arg1='foo', arg2=42)
        self.assertEqual((
            ('http://write.url',
             'json=%7B%22params%22%3A+%7B%22arg1%22%3A+%22foo%22%2C+%22arg2'
             '%22%3A+42%2C+%22token%22%3A+%22my-write-token%22%7D%2C+%22method'
             '%22%3A+%22my-command%22%7D'),
            dict(timeout=4711.0)), urlopen.call_args)
        self.assertEqual(u'okay', result)

    def test_post_does_nothing_if_write_token_is_disabled(self):
        conn = zeit.brightcove.connection.APIConnection(
            None, 'disabled', None, None, None)
        with mock.patch('urllib2.urlopen') as urlopen:
            conn.post('my-command', arg1='foo', arg2=42)
        self.assertFalse(urlopen.called)
