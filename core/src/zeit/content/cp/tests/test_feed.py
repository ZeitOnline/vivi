# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.content.cp.interfaces
import zope.schema.interfaces


class FeedTest(unittest.TestCase):

    def test_constraint(self):
        v = zeit.content.cp.interfaces.valid_feed_url
        self.assertTrue(v('http://foo.bar/baz'))
        self.assertTrue(v('https://foo.bar/baz'))
        self.assertTrue(v('file:///foo.bar/baz'))
        self.assertRaises(zeit.content.cp.interfaces.InvalidFeedURL,
                          v, 'feed://foo.bar/baz')
        self.assertRaises(zope.schema.interfaces.InvalidURI,
                          v, 'foo.bar/baz')
        self.assertRaises(zope.schema.interfaces.InvalidURI,
                          v, 'asdkjfa')


def test_suite():
    return unittest.makeSuite(FeedTest)
