# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.brightcove.testing import PLAYLIST_LIST_RESPONSE
from zeit.brightcove.testing import VIDEO_1234, PLAYLIST_2345
from zeit.brightcove.update import update_from_brightcove
from zeit.cms.workflow.interfaces import PRIORITY_LOW
import copy
import datetime
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
        self.old_video = copy.deepcopy(VIDEO_1234)
        self.old_playlist = copy.deepcopy(PLAYLIST_2345)

    def tearDown(self):
        zeit.brightcove.testing.RequestHandler.sleep = 0
        VIDEO_1234.update(self.old_video)
        PLAYLIST_2345.clear()
        PLAYLIST_2345.update(self.old_playlist)
        super(UpdateVideoTest, self).tearDown()

    def test_new_video_in_bc_should_be_added_to_repository(self):
        # hack around test setup
        del self.repository['video']['2010-03']['1234']

        update_from_brightcove()
        transaction.commit()
        zeit.workflow.testing.run_publish(PRIORITY_LOW)

        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        self.assertEqual(
            u'Starrummel auf dem Roten Teppich zur 82. Oscar-Verleihung',
            video.title)
        info = zeit.cms.workflow.interfaces.IPublishInfo(video)
        self.assertTrue(info.published)

    def test_new_ignored_video_in_bc_should_not_be_added_to_repository(self):
        # hack around test setup
        del self.repository['video']['2010-03']['1234']
        VIDEO_1234['customFields']['ignore_for_update'] = '1'

        update_from_brightcove()
        transaction.commit()
        zeit.workflow.testing.run_publish(PRIORITY_LOW)
        self.assertFalse('1234' in self.repository['video']['2010-03'])

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

    def test_updated_relateds_should_overwrite_local_data_with_newer_bc_edits(
        self):
        from zeit.cms.related.interfaces import IRelatedContent
        soon = str(int((time.time() + 10) * 1000))
        VIDEO_1234['lastModifiedDate'] = soon
        update_from_brightcove()
        VIDEO_1234['customFields']['ref_link1'] = (
            'http://xml.zeit.de/online/2007/01/Somalia')
        soon = str(int((time.time() + 10) * 1000))
        VIDEO_1234['lastModifiedDate'] = soon
        update_from_brightcove()

        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        related = IRelatedContent(video)
        self.assertEqual(
            ['http://xml.zeit.de/online/2007/01/Somalia'],
            [x.uniqueId for x in related.related])

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
        VIDEO_1234['lastModifiedDate'] = '1268053197834'
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
        zeit.workflow.testing.run_publish(PRIORITY_LOW)

        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        info = zeit.cms.workflow.interfaces.IPublishInfo(video)
        self.assertTrue(info.published)
        self.assertGreater(info.date_last_published, last_published)

    def test_videos_should_only_be_published_once_per_run(self):
        VIDEO_1234['name'] = u'upstream change'
        soon = str(int((time.time() + 10) * 1000))
        VIDEO_1234['lastModifiedDate'] = soon
        with mock.patch(
            'zeit.cms.workflow.interfaces.IPublish') as publish:
            update_from_brightcove()
        self.assertEqual(u'http://xml.zeit.de/video/2010-03/1234',
                         publish.call_args[0][0].uniqueId)  # Safety belt
        self.assertEqual(1, publish().publish.call_count)

    def test_unpublished_videos_should_be_published(self):
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        info = zeit.cms.workflow.interfaces.IPublishInfo(video)
        info.published = False
        update_from_brightcove()
        zeit.workflow.testing.run_publish(PRIORITY_LOW)
        info = zeit.cms.workflow.interfaces.IPublishInfo(video)
        self.assertTrue(info.published)

    def test_published_but_changed_videos_should_be_published_again(self):
        # this behaviour is useful in problematic cases such as
        # 1. update_from_brightcove: new video
        # 2. publish of said video fails for some reason
        # 3. update_from_brightcove: no changes, but we should try to publish
        #    again so the changes from (1) become visible
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        info = zeit.cms.workflow.interfaces.IPublishInfo(video)
        info.published = True
        # force last_published < last_modified
        info.date_last_published -= datetime.timedelta(hours=1)
        last_published = info.date_last_published

        update_from_brightcove()
        zeit.workflow.testing.run_publish(PRIORITY_LOW)
        info = zeit.cms.workflow.interfaces.IPublishInfo(video)
        self.assertGreater(info.date_last_published, last_published)

    def test_deleted_and_not_published_should_be_deleted_from_cms(self):
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        zeit.cms.workflow.interfaces.IPublishInfo(video).published = False
        VIDEO_1234['itemState'] = 'DELETED'
        soon = str(int((time.time() + 10) * 1000))
        VIDEO_1234['lastModifiedDate'] = soon
        update_from_brightcove()
        self.assertIsNone(zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234', None))

    def test_deleted_and_published_should_be_retracted(self):
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        zeit.cms.workflow.interfaces.IPublishInfo(video).published = True
        VIDEO_1234['itemState'] = 'DELETED'
        soon = str(int((time.time() + 10) * 1000))
        VIDEO_1234['lastModifiedDate'] = soon
        with mock.patch('zeit.workflow.publish.Publish.retract') as retract:
            update_from_brightcove()
            self.assertTrue(retract.called)

    def test_deleted_and_published_should_not_be_deleted(self):
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        zeit.cms.workflow.interfaces.IPublishInfo(video).published = True
        VIDEO_1234['itemState'] = 'DELETED'
        soon = str(int((time.time() + 10) * 1000))
        VIDEO_1234['lastModifiedDate'] = soon
        update_from_brightcove()
        self.assertIsNotNone(zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234', None))

    def test_deleted_videos_should_not_be_imported(self):
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        del video.__parent__[video.__name__]
        VIDEO_1234['itemState'] = 'DELETED'
        soon = str(int((time.time() + 10) * 1000))
        VIDEO_1234['lastModifiedDate'] = soon
        update_from_brightcove()
        self.assertIsNone(zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234', None))

    def test_inactive_and_published_video_should_be_retracted(self):
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        zeit.cms.workflow.interfaces.IPublishInfo(video).published = True
        VIDEO_1234['itemState'] = 'INACTIVE'
        soon = str(int((time.time() + 10) * 1000))
        VIDEO_1234['lastModifiedDate'] = soon
        with mock.patch('zeit.workflow.publish.Publish.retract') as retract:
            update_from_brightcove()
            retract.assert_called_with(PRIORITY_LOW)

    def test_inactive_and_not_published_video_should_not_be_retracted(self):
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        zeit.cms.workflow.interfaces.IPublishInfo(video).published = False
        VIDEO_1234['itemState'] = 'INACTIVE'
        soon = str(int((time.time() + 10) * 1000))
        VIDEO_1234['lastModifiedDate'] = soon
        with mock.patch('zeit.workflow.publish.Publish.retract') as retract:
            update_from_brightcove()
            self.assertFalse(retract.called)

    def test_inactive_video_should_not_be_deleted(self):
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        zeit.cms.workflow.interfaces.IPublishInfo(video).published = False
        VIDEO_1234['itemState'] = 'INACTIVE'
        soon = str(int((time.time() + 10) * 1000))
        VIDEO_1234['lastModifiedDate'] = soon
        update_from_brightcove()
        self.assertIsNotNone(zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234', None))

    def test_inactive_videos_should_be_imported_but_not_published(self):
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        del video.__parent__[video.__name__]
        VIDEO_1234['itemState'] = 'INACTIVE'
        soon = str(int((time.time() + 10) * 1000))
        VIDEO_1234['lastModifiedDate'] = soon
        with mock.patch('zeit.workflow.publish.Publish.publish') as publish:
            update_from_brightcove()
            self.assertFalse(publish.called)

    def test_deleted_videos_not_in_cms_should_be_left_alone(self):
        video = zeit.cms.interfaces.ICMSContent(

            'http://xml.zeit.de/video/2010-03/1234')
        del video.__parent__[video.__name__]

        VIDEO_1234['itemState'] = 'DELETED'
        soon = str(int((time.time() + 10) * 1000))
        VIDEO_1234['lastModifiedDate'] = soon

        update_from_brightcove()

        self.assertIsNone(zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234', None))

    def test_timeout_should_not_block_but_raise(self):
        import urllib2
        import zope.component
        zeit.brightcove.testing.RequestHandler.sleep = 1
        connection = zope.component.getUtility(
            zeit.brightcove.interfaces.IAPIConnection)
        timeout = connection.timeout
        connection.timeout = 0.5

        def reset():
            connection.timeout = timeout
        self.addCleanup(reset)

        self.assertRaises(
            urllib2.URLError, lambda: update_from_brightcove())

    def test_ignore_for_update_should_not_update_repository(self):
        VIDEO_1234['customFields']['ignore_for_update'] = '1'
        soon = str(int((time.time() + 10) * 1000))
        VIDEO_1234['lastModifiedDate'] = soon
        VIDEO_1234['name'] = 'test title'
        update_from_brightcove()
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        self.assertEquals(
            'Starrummel auf dem Roten Teppich zur 82. Oscar-Verleihung',
            video.title)


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
        zeit.workflow.testing.run_publish(PRIORITY_LOW)

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

    def test_changed_videoids_should_be_written(self):
        PLAYLIST_2345['videoIds'] = [1234]
        update_from_brightcove()
        playlist = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/playlist/2345')
        self.assertEqual(
            ['http://xml.zeit.de/video/2010-03/1234'],
            [v.uniqueId for v in playlist.videos])

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
        zeit.workflow.testing.run_publish(PRIORITY_LOW)

        playlist = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/playlist/2345')
        info = zeit.cms.workflow.interfaces.IPublishInfo(playlist)
        self.assertTrue(info.published)
        self.assertGreater(info.date_last_published, last_published)

    def test_unpublished_playlists_should_be_published(self):
        pls = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/playlist/2345')
        info = zeit.cms.workflow.interfaces.IPublishInfo(pls)
        info.published = False
        update_from_brightcove()
        zeit.workflow.testing.run_publish(PRIORITY_LOW)
        info = zeit.cms.workflow.interfaces.IPublishInfo(pls)
        self.assertTrue(info.published)

    def test_published_but_changed_playlists_should_be_published_again(self):
        playlist = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/playlist/2345')
        info = zeit.cms.workflow.interfaces.IPublishInfo(playlist)
        info.published = True
        # force last_published < last_modified
        info.date_last_published -= datetime.timedelta(hours=1)
        last_published = info.date_last_published

        update_from_brightcove()
        zeit.workflow.testing.run_publish(PRIORITY_LOW)
        info = zeit.cms.workflow.interfaces.IPublishInfo(playlist)
        self.assertGreater(info.date_last_published, last_published)

    def test_deleted_and_not_published_should_be_deleted_from_cms(self):
        playlist = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/playlist/3456')
        info = zeit.cms.workflow.interfaces.IPublishInfo(playlist)
        info.published = False

        del PLAYLIST_LIST_RESPONSE['items'][-1]
        update_from_brightcove()
        self.assertIsNone(zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/playlist/3456', None))

    def test_deleted_and_published_should_be_retracted(self):
        playlist = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/playlist/3456')
        info = zeit.cms.workflow.interfaces.IPublishInfo(playlist)
        info.published = True

        del PLAYLIST_LIST_RESPONSE['items'][-1]
        update_from_brightcove()
        zeit.workflow.testing.run_publish(PRIORITY_LOW)
        info = zeit.cms.workflow.interfaces.IPublishInfo(playlist)
        self.assertFalse(info.published)

    def test_deleted_and_published_should_not_be_deleted(self):
        playlist = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/playlist/3456')
        info = zeit.cms.workflow.interfaces.IPublishInfo(playlist)
        info.published = True

        del PLAYLIST_LIST_RESPONSE['items'][-1]
        update_from_brightcove()
        self.assertIsNotNone(zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/playlist/3456', None))
