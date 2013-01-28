# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.testing.mock
import json
import zeit.brightcove.testing
import zeit.cms.tagging.testing
import zeit.cms.testing


class UpdateItem(zeit.cms.testing.BrowserTestCase,
                 zeit.cms.tagging.testing.TaggingHelper):

    layer = zeit.brightcove.testing.BrightcoveLayer

    def setUp(self):
        super(UpdateItem, self).setUp()
        self.setup_tags()
        self.patches = gocept.testing.mock.Patches()
        self.publish = self.patches.add(
            'zeit.cms.workflow.interfaces.IPublish')
        self.publish().publish.return_value = 9876

    def tearDown(self):
        self.patches.reset()
        super(UpdateItem, self).tearDown()

    def test_update_playlist(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/'
               '@@update-brightcove-item?playlist_id=2345')
        result = json.loads(b.contents)
        self.assertEqual(
            dict(publish_job=9876, changed=True, error=None),
            result)

    def test_update_video(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/'
               '@@update-brightcove-item?video_id=1234')
        result = json.loads(b.contents)
        self.assertEqual(
            dict(publish_job=9876, changed=True, error=None),
            result)

    def test_exception_is_returned_as_error_message(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/'
               '@@update-brightcove-item?playlist_id=9988')
        result = json.loads(b.contents)
        self.assertEqual(dict(
                error='ValueError: playlist_id=9988 not found in Brightcove.'),
            result)
