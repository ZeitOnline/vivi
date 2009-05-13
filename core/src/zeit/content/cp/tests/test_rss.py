# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.interfaces
import zope.component
import unittest
import zeit.content.cp.testing

class FeedTest(zeit.content.cp.testing.FunctionalTestCase):

    def test_only_one_feed_object_per_url(self):
        fm = zope.component.getUtility(zeit.content.cp.interfaces.IFeedManager)
        self.assertEquals(fm.get_feed('foobar'), fm.get_feed('foobar'))
        self.assertNotEqual(fm.get_feed('foo'), fm.get_feed('foobar'))

def test_suite():
    return unittest.makeSuite(FeedTest)
