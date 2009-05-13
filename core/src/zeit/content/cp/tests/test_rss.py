# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.feed import Feed
import unittest
import zeit.content.cp.testing

class FeedTest(zeit.content.cp.testing.FunctionalTestCase):

    def test_only_one_feed_object_per_url(self):
        self.assertEquals(Feed.get_feed('foobar'), Feed.get_feed('foobar'))
        self.assertNotEqual(Feed.get_feed('foo'), Feed.get_feed('foobar'))

def test_suite():
    return unittest.makeSuite(FeedTest)
