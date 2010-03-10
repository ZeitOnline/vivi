# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import time
import transaction
import zeit.brightcove.interfaces
import zeit.brightcove.testing
import zeit.cms.interfaces
import zope.component


class RepositoryTest(zeit.brightcove.testing.BrightcoveTestCase):

    def tearDown(self):
        try:
            del self.repository.BRIGHTCOVE_CACHE_TIMEOUT
        except AttributeError:
            pass
        super(RepositoryTest, self).tearDown()

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.brightcove.interfaces.IRepository)

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
        video = self.repository['video:1234']
        self.assertTrue(zeit.brightcove.interfaces.IVideo.providedBy(video))

    def test_brightcove_cache_timeout(self):
        # Set the timeout to 2 seconds
        self.repository.BRIGHTCOVE_CACHE_TIMEOUT = datetime.timedelta(
            seconds=2)
        # Get video, modify and commit. The changes are visible for 2 seconds.
        # After that they're gone because we're not *really* changing the data
        video = self.repository['video:1234']
        video.subtitle = u'A new subtitle'
        transaction.commit()
        time.sleep(1)
        # Still old data
        video = self.repository['video:1234']
        self.assertEquals(u'A new subtitle', video.subtitle)
        time.sleep(1)
        # Now we've got "new" data from brightcove
        video = self.repository['video:1234']
        self.assertEquals(
            u'Mehr Glanz, Glamour und erwartungsvolle Spannung',
            video.subtitle)
