# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest
import zeit.cms.interfaces
import zeit.content.cp.interfaces
import zeit.content.cp.testing
import zope.schema.interfaces


class FeedTest(unittest.TestCase):

    def test_constraint(self):
        v = zeit.content.cp.interfaces.valid_feed_url
        self.assertTrue(v('http://foo.bar/baz'))
        self.assertTrue(v('https://foo.bar/baz'))
        self.assertTrue(v('file:///foo.bar/baz'))
        self.assertRaises(zeit.cms.interfaces.ValidationError,
                          v, 'feed://foo.bar/baz')
        self.assertRaises(zope.schema.interfaces.InvalidURI,
                          v, 'foo.bar/baz')
        self.assertRaises(zope.schema.interfaces.InvalidURI,
                          v, 'asdkjfa')


class TestFeedDownload(zeit.content.cp.testing.FunctionalTestCase):

    layer = zeit.content.cp.testing.FEED_SERVER_LAYER

    def test_download_should_abort_after_timeout(self):
        from ..feed import Feed
        feed = Feed()
        feed.url = 'http://localhost:%s/heise.xml' % self.layer['http_port']
        with mock.patch('zeit.content.cp.feed.DOWNLOAD_TIMEOUT', new=1):
            with mock.patch('zeit.content.cp.testing.RequestHandler.'
                            'delay_request_by', new=2):
                feed.fetch_and_convert()
        self.assertIn('Timeout', feed.error)
