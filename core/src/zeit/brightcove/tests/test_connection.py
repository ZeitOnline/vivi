# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.brightcove.connection


class ConnectionTest(unittest.TestCase):

    def test_strings_should_be_read_from_json_as_unicode(self):
        conn = zeit.brightcove.connection.APIConnection(
            None, None, None, None)
        response = conn.decode_broken_brightcove_json('{"foo": "bar"}')
        self.assertTrue(isinstance(response.iterkeys().next(), unicode))
        self.assertTrue(isinstance(response.itervalues().next(), unicode))
