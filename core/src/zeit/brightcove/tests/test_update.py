# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.brightcove.testing import VIDEO_1234, PLAYLIST_2345
from zeit.brightcove.testing import PLAYLIST_LIST_RESPONSE
import time
import transaction
import zeit.brightcove.interfaces
import zeit.brightcove.testing
import zope.lifecycleevent


class RepositoryTest(zeit.brightcove.testing.BrightcoveTestCase):

    def setUp(self):
        super(RepositoryTest, self).setUp()
        self.old_video = VIDEO_1234.copy()
        self.old_playlist = PLAYLIST_2345.copy()
        self.old_playlist_items = PLAYLIST_LIST_RESPONSE['items'][:]

    def tearDown(self):
        VIDEO_1234.update(self.old_video)
        PLAYLIST_2345.update(self.old_playlist)
        PLAYLIST_LIST_RESPONSE['items'] = self.old_playlist_items
        super(RepositoryTest, self).tearDown()

    def test_cronjob_should_not_overwrite_user_edits(self):
        video = self.repository['video-1234']
        video.title = u'changed'
        video = self.repository['video-1234']
        self.assertEqual(u'changed', video.title)
        zope.lifecycleevent.modified(video)
        transaction.commit()
        video = self.repository['video-1234']
        self.assertEqual(u'changed', video.title)
        self.repository.update_from_brightcove()
        video = self.repository['video-1234']
        self.assertEqual(u'changed', video.title)

    def test_cronjob_should_fetch_changes_from_brightcove(self):
        video = self.repository['video-1234']
        video.title = u'local change'
        # update local modification timestamp
        zope.lifecycleevent.modified(video)
        transaction.commit()

        # as long as the modified date is not newer than the local one,
        # upstream changes are ignored
        VIDEO_1234['name'] = u'upstream change'
        self.repository.update_from_brightcove()
        video = self.repository['video-1234']
        self.assertEqual(u'local change', video.title)
        
        soon = str(int((time.time() + 10) * 1000))
        VIDEO_1234['lastModifiedDate'] = soon
        self.repository.update_from_brightcove()
        video = self.repository['video-1234']
        self.assertEqual(u'upstream change', video.title)
        

        # Playlists don't have a modified date,
        # so changes propagate immediately
        playlist = self.repository['playlist-2345']
        self.assertEqual(u'Videos zum Thema Film', playlist.title)
        PLAYLIST_2345['name'] = u'another change'
        self.repository.update_from_brightcove()
        playlist = self.repository['playlist-2345']
        self.assertEqual(u'another change', playlist.title)

    def test_fetch_changes_from_bc_if_video_still_differs(self):
        video = self.repository['video-1234']
        video.title = u'local change'
        # update local modification timestamp
        zope.lifecycleevent.modified(video)
        transaction.commit()

        #video_still property update might not correspond to the update time 
        VIDEO_1234['name'] = u'upstream change'
        VIDEO_1234['videoStillURL'] = 'http://videostillurl2'
        self.repository.update_from_brightcove()
        video = self.repository['video-1234']
        self.assertEqual(u'upstream change', video.title)

    def test_if_local_data_equals_brightcove_it_should_not_be_written(self):
        video = self.repository['video-1234']
        video.marker = True
        playlist = self.repository['playlist-2345']
        playlist.marker = True

        VIDEO_1234['lastModifiedDate'] = str(int((time.time() + 10) * 1000))
        self.repository.update_from_brightcove()
        video = self.repository['video-1234']
        self.assertTrue(video.marker)
        playlist = self.repository['playlist-2345']
        self.assertTrue(playlist.marker)

    def test_deleting_playlist_from_brightcove(self):
        playlist = self.repository['playlist-3456']
        self.assertTrue(
            zeit.brightcove.interfaces.IPlaylist.providedBy(playlist))

        del PLAYLIST_LIST_RESPONSE['items'][-1]

        self.repository.update_from_brightcove()
        pls = self.repository['playlist-3456']
        self.assertEquals('DELETED', pls.item_state)
