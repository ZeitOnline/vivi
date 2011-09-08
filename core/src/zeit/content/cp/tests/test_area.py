# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest


class TestContentIter(unittest.TestCase):

    def test_unresolveable_blocks_should_not_be_adapted(self):
        from zeit.content.cp.area import cms_content_iter
        area = mock.Mock()
        area.values = mock.Mock(
            return_value=[mock.sentinel.block1,
                          None,
                          mock.sentinel.block2])
        with mock.patch('zeit.content.cp.interfaces.ICMSContentIterable') as \
            ci:
            cms_content_iter(area)
            self.assertEqual(2, ci.call_count)
            self.assertEqual(
                [((mock.sentinel.block1, ), {}),
                 ((mock.sentinel.block2, ), {})],
                ci.call_args_list)
