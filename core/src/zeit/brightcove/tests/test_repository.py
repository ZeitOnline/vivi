# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.brightcove.testing import VIDEO_1234
import time
import transaction
import zeit.brightcove.interfaces
import zeit.brightcove.testing
import zeit.cms.interfaces
import zope.lifecycleevent


class RepositoryTest(zeit.brightcove.testing.BrightcoveTestCase):

    def setUp(self):
        super(RepositoryTest, self).setUp()
        self.old_video = VIDEO_1234.copy()

    def tearDown(self):
        VIDEO_1234.update(self.old_video)
        super(RepositoryTest, self).tearDown()

    def test_invalid_id(self):
        self.assertRaises(KeyError,
                          self.repository.__getitem__, 'video:invalid')
        self.assertRaises(KeyError,
                          self.repository.__getitem__, 'iuj2480hasf')
        self.assertRaises(KeyError,
                          self.repository.__getitem__, 'playlist:2345723')
        self.assertRaises(KeyError,
                          self.repository.__getitem__, 'video:2345723')

    def test_getitem(self):
        self.repository._data.clear()
        self.assertRaises(KeyError, self.repository.__getitem__, 'video:1234')
        self.repository.update_from_brightcove()
        video = self.repository['video:1234']
        self.assertTrue(zeit.brightcove.interfaces.IVideo.providedBy(video))

    def test_cronjob_should_not_overwrite_user_edits(self):
        self.repository.update_from_brightcove()
        video = self.repository['video:1234']
        video.title = u'changed'
        video = self.repository['video:1234']
        self.assertEqual(u'changed', video.title)
        zope.lifecycleevent.modified(video)
        transaction.commit()
        video = self.repository['video:1234']
        self.assertEqual(u'changed', video.title)
        self.repository.update_from_brightcove()
        video = self.repository['video:1234']
        self.assertEqual(u'changed', video.title)

    def test_cronjob_should_fetch_changes_from_brightcove(self):
        self.repository.update_from_brightcove()
        video = self.repository['video:1234']
        video.title = u'local change'
        zope.lifecycleevent.modified(video)
        transaction.commit()

        # as long as the modified date is not newer than the local one,
        # upstream changes are ignored
        VIDEO_1234['name'] = u'upstream change'
        self.repository.update_from_brightcove()
        video = self.repository['video:1234']
        self.assertEqual(u'local change', video.title)

        VIDEO_1234['lastModifiedDate'] = str(int((time.time() + 10) * 1000))
        self.repository.update_from_brightcove()
        video = self.repository['video:1234']
        self.assertEqual(u'upstream change', video.title)
