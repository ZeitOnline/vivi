# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.brightcove.testing import VIDEO_1234, PLAYLIST_2345
from zeit.brightcove.testing import PLAYLIST_LIST_RESPONSE
import mock
import time
import zeit.brightcove.interfaces
import zeit.brightcove.testing
import zeit.cms.checkout.helper
import zope.component


def run_update():
    zope.component.getUtility(zeit.brightcove.interfaces.IUpdate)()


class UpdateVideoTest(zeit.brightcove.testing.BrightcoveTestCase):

    def setUp(self):
        super(UpdateVideoTest, self).setUp()
        self.old_video = VIDEO_1234.copy()

    def tearDown(self):
        VIDEO_1234.update(self.old_video)
        super(UpdateVideoTest, self).tearDown()

    def test_new_video_in_bc_should_be_added_to_repository(self):
        # hack around test setup
        del self.repository['brightcove-folder']['video-1234']

        run_update()

        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/brightcove-folder/video-1234')
        self.assertEqual(
            u'Starrummel auf dem Roten Teppich zur 82. Oscar-Verleihung',
            video.title)

    def test_update_should_not_overwrite_local_edits_with_old_bc_data(self):
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/brightcove-folder/video-1234')
        with zeit.cms.checkout.helper.checked_out(
                video, semantic_change=True) as co:
            co.title = u'local change'

        VIDEO_1234['name'] = u'upstream change'
        run_update()

        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/brightcove-folder/video-1234')
        self.assertEqual(u'local change', video.title)

    def test_update_should_overwrite_local_data_with_newer_bc_edits(self):
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/brightcove-folder/video-1234')
        with zeit.cms.checkout.helper.checked_out(
            video, semantic_change=True) as co:
            co.title = u'local change'

        VIDEO_1234['name'] = u'upstream change'
        soon = str(int((time.time() + 10) * 1000))
        VIDEO_1234['lastModifiedDate'] = soon

        run_update()

        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/brightcove-folder/video-1234')
        self.assertEqual(u'upstream change', video.title)

    def test_difference_of_video_still_counts_as_newer_upstream_edit(self):
        # A bug in Brightcove may cause the last-modified date to remain
        # unchanged even when the video-still URL is actually changed.
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/brightcove-folder/video-1234')
        with zeit.cms.checkout.helper.checked_out(video) as co:
            co.title = u'local change'

        VIDEO_1234['name'] = u'upstream change'
        VIDEO_1234['videoStillURL'] = 'http://videostillurl2'

        run_update()

        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/brightcove-folder/video-1234')
        self.assertEqual(u'upstream change', video.title)

    def test_if_local_data_equals_brightcove_it_should_not_be_written(self):
        VIDEO_1234['lastModifiedDate'] = str(int((time.time() + 10) * 1000))
        with mock.patch('zeit.brightcove.content.Video.to_cms') as to_cms:
            run_update()
            self.assertFalse(to_cms.called)

    def test_videos_in_deleted_state_should_be_deleted_from_cms(self):
        self.assertIsNotNone(zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/brightcove-folder/video-1234', None))

        VIDEO_1234['itemState'] = 'DELETED'
        soon = str(int((time.time() + 10) * 1000))
        VIDEO_1234['lastModifiedDate'] = soon

        run_update()

        self.assertIsNone(zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/brightcove-folder/video-1234', None))


class UpdatePlaylistTest(zeit.brightcove.testing.BrightcoveTestCase):

    def setUp(self):
        super(UpdatePlaylistTest, self).setUp()
        self.old_playlist = PLAYLIST_2345.copy()
        self.old_playlist_items = PLAYLIST_LIST_RESPONSE['items'][:]

    def tearDown(self):
        PLAYLIST_2345.update(self.old_playlist)
        PLAYLIST_LIST_RESPONSE['items'] = self.old_playlist_items
        super(UpdatePlaylistTest, self).tearDown()

    def test_new_playlist_in_bc_should_be_added_to_repository(self):
        # hack around test setup
        del self.repository['brightcove-folder']['playlist-2345']

        run_update()

        playlist = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/brightcove-folder/playlist-2345')
        self.assertEqual('Videos zum Thema Film', playlist.title)

    def test_update_always_overwrites_local_data_with_bc_data(self):
        playlist = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/brightcove-folder/playlist-2345')
        with zeit.cms.checkout.helper.checked_out(
            playlist, semantic_change=True) as co:
            co.title = u'local change'

        PLAYLIST_2345['name'] = u'upstream change'

        run_update()

        playlist = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/brightcove-folder/playlist-2345')
        self.assertEqual(u'upstream change', playlist.title)

    def test_if_local_data_equals_brightcove_it_should_not_be_written(self):
        with mock.patch('zeit.brightcove.content.Playlist.to_cms') as to_cms:
            run_update()
            self.assertFalse(to_cms.called)

    def test_playlist_no_longer_in_brightcove_is_deleted_from_cms(self):
        self.assertIsNotNone(zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/brightcove-folder/playlist-3456', None))

        del PLAYLIST_LIST_RESPONSE['items'][-1]

        run_update()

        self.assertIsNone(zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/brightcove-folder/playlist-3456', None))
