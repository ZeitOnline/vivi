# Copyright (c) 2011-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.brightcove.connection


class ConnectionTest(unittest.TestCase):

    def test_strings_should_be_read_from_json_as_unicode(self):
        conn = zeit.brightcove.connection.APIConnection(
            None, None, None, None, None)
        response = conn.parse_json('{"foo": "bar"}')
        self.assertTrue(isinstance(response.iterkeys().next(), unicode))
        self.assertTrue(isinstance(response.itervalues().next(), unicode))

    def test_json_invalid_characters_are_removed_from_json_data(self):
        conn = zeit.brightcove.connection.APIConnection(
            None, None, None, None, None)
        response = conn.parse_json('{"foo": "\x09"}')
        self.assertEqual('', response['foo'])

    def test_xml_restricted_characters_are_removed_from_json_data(self):
        conn = zeit.brightcove.connection.APIConnection(
            None, None, None, None, None)
        response = conn.parse_json('{"foo": "\x7f"}')
        self.assertEqual('', response['foo'])
