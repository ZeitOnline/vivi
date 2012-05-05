# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest2 as unittest


class HistoryTest(unittest.TestCase):

    def test_history_should_urlencoe_tid(self):
        from zeit.edit.browser.undo import History
        h = History()
        h.context, h.request = mock.Mock(), mock.Mock()
        h.url = mock.Mock()
        with mock.patch('zeit.edit.interfaces.IUndo') as undo:
            undo().history = [
                dict(description='', tid='\x03\x8f\xa2\x8f\xf7\x99v\xaa')]
            result = h.json()
        self.assertEqual('A4%2Bij/eZdqo%3D%0A', result['history'][0]['tid'])


class RevertTest(unittest.TestCase):

    def test_revert_should_urldecode_tid(self):
        from zeit.edit.browser.undo import Revert
        r = Revert()
        r.context, r.request = mock.Mock(), mock.Mock()
        r.signals = []
        r.tid = 'A4%2Bij/eZdqo%3D%0A'
        with mock.patch('zeit.edit.interfaces.IUndo') as undo:
            undo().history = ()
            r.update()
            undo.assert_called_with_args('\x03\x8f\xa2\x8f\xf7\x99v\xaa')
