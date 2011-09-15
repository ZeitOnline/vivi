# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.brightcove.testing import PLAYLIST_LIST_RESPONSE
from zeit.brightcove.testing import VIDEO_1234, PLAYLIST_2345
from zeit.brightcove.update import update_from_brightcove
import mock
import time
import transaction
import zeit.brightcove.testing
import zeit.cms.checkout.helper
import zeit.cms.workflow.interfaces
import zeit.workflow.testing


class UpdateVideoTest(zeit.brightcove.testing.BrightcoveTestCase):

    def setUp(self):
        super(UpdateVideoTest, self).setUp()
        self.old_video = VIDEO_1234.copy()

    def tearDown(self):
        VIDEO_1234.update(self.old_video)
        super(UpdateVideoTest, self).tearDown()

    def test_new_video_in_bc_should_be_added_to_repository(self):
        # hack around test setup
        del self.repository['video']['2010-03']['1234']

        update_from_brightcove()
        transaction.commit()
        zeit.workflow.testing.run_publish()

        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        self.assertEqual(
            u'Starrummel auf dem Roten Teppich zur 82. Oscar-Verleihung',
            video.title)
        info = zeit.cms.workflow.interfaces.IPublishInfo(video)
        self.assertTrue(info.published)

    def test_update_should_not_overwrite_local_edits_with_old_bc_data(self):
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        with zeit.cms.checkout.helper.checked_out(
                video, semantic_change=True) as co:
            co.title = u'local change'

        VIDEO_1234['name'] = u'upstream change'
        update_from_brightcove()

        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        self.assertEqual(u'local change', video.title)

    def test_update_should_overwrite_local_data_with_newer_bc_edits(self):
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        with zeit.cms.checkout.helper.checked_out(
            video, semantic_change=True) as co:
            co.title = u'local change'

        VIDEO_1234['name'] = u'upstream change'
        soon = str(int((time.time() + 10) * 1000))
        VIDEO_1234['lastModifiedDate'] = soon

        update_from_brightcove()

        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        self.assertEqual(u'upstream change', video.title)

    def test_difference_of_video_still_counts_as_newer_upstream_edit(self):
        # A bug in Brightcove may cause the last-modified date to remain
        # unchanged even when the video-still URL is actually changed.
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        with zeit.cms.checkout.helper.checked_out(video) as co:
            co.title = u'local change'

        VIDEO_1234['name'] = u'upstream change'
        VIDEO_1234['videoStillURL'] = 'http://videostillurl2'

        update_from_brightcove()

        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        self.assertEqual(u'upstream change', video.title)

    def test_if_local_data_equals_brightcove_it_should_not_be_written(self):
        VIDEO_1234['lastModifiedDate'] = str(int((time.time() + 10) * 1000))
        with mock.patch('zeit.cms.checkout.manager.CheckoutManager.checkin'
                        ) as checkin:
            update_from_brightcove()
            self.assertFalse(checkin.called)

    def test_should_publish_after_update(self):
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        last_published = zeit.cms.workflow.interfaces.IPublishInfo(
            video).date_last_published
        zeit.cms.workflow.interfaces.IPublish(video).retract()

        VIDEO_1234['name'] = u'upstream change'
        soon = str(int((time.time() + 10) * 1000))
        VIDEO_1234['lastModifiedDate'] = soon
        update_from_brightcove()
        transaction.commit()
        zeit.workflow.testing.run_publish()

        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        info = zeit.cms.workflow.interfaces.IPublishInfo(video)
        self.assertTrue(info.published)
        self.assertGreater(info.date_last_published, last_published)

    def test_videos_in_deleted_state_should_be_deleted_from_cms(self):
        self.assertIsNotNone(zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234', None))

        VIDEO_1234['itemState'] = 'DELETED'
        soon = str(int((time.time() + 10) * 1000))
        VIDEO_1234['lastModifiedDate'] = soon

        update_from_brightcove()

        self.assertIsNone(zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234', None))

    def test_deleted_video_should_be_retracted(self):
        VIDEO_1234['itemState'] = 'DELETED'
        soon = str(int((time.time() + 10) * 1000))
        VIDEO_1234['lastModifiedDate'] = soon
        with mock.patch('zeit.workflow.publish.Publish.retract') as retract:
            update_from_brightcove()
            self.assertTrue(retract.called)


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
        del self.repository['video']['playlist']['2345']

        update_from_brightcove()
        transaction.commit()
        zeit.workflow.testing.run_publish()

        playlist = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/playlist/2345')
        self.assertEqual('Videos zum Thema Film', playlist.title)
        info = zeit.cms.workflow.interfaces.IPublishInfo(playlist)
        self.assertTrue(info.published)

    def test_update_always_overwrites_local_data_with_bc_data(self):
        playlist = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/playlist/2345')
        with zeit.cms.checkout.helper.checked_out(
            playlist, semantic_change=True) as co:
            co.title = u'local change'

        PLAYLIST_2345['name'] = u'upstream change'

        update_from_brightcove()

        playlist = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/playlist/2345')
        self.assertEqual(u'upstream change', playlist.title)

    def test_if_local_data_equals_brightcove_it_should_not_be_written(self):
        with mock.patch('zeit.brightcove.converter.Playlist.to_cms') as to_cms:
            update_from_brightcove()
            self.assertFalse(to_cms.called)

    def test_should_publish_after_update(self):
        playlist = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/playlist/2345')
        last_published = zeit.cms.workflow.interfaces.IPublishInfo(
            playlist).date_last_published
        zeit.cms.workflow.interfaces.IPublish(playlist).retract()

        PLAYLIST_2345['name'] = u'upstream change'
        update_from_brightcove()
        transaction.commit()
        zeit.workflow.testing.run_publish()

        playlist = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/playlist/2345')
        info = zeit.cms.workflow.interfaces.IPublishInfo(playlist)
        self.assertTrue(info.published)
        self.assertGreater(info.date_last_published, last_published)

    def test_playlist_no_longer_in_brightcove_is_deleted_from_cms(self):
        self.assertIsNotNone(zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/playlist/3456', None))

        del PLAYLIST_LIST_RESPONSE['items'][-1]

        update_from_brightcove()

        self.assertIsNone(zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/playlist/3456', None))

    def test_deleted_playlist_should_be_retracted(self):
        del PLAYLIST_LIST_RESPONSE['items'][-1]
        with mock.patch('zeit.workflow.publish.Publish.retract') as retract:
            update_from_brightcove()
            self.assertTrue(retract.called)
