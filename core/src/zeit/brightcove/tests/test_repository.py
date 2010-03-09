# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import time
import transaction
import zeit.brightcove.interfaces
import zeit.brightcove.testing
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
        self.assertEquals(
            u'Starrummel auf dem Roten Teppich zur 82. Oscar-Verleihung',
            video.title)
        self.assertEquals(
            u'Glanz, Glamour und erwartungsvolle Spannung',
            video.teaserText)
        self.assertEquals(
            u'Mehr Glanz, Glamour und erwartungsvolle Spannung',
            video.subtitle)
        self.assertEquals(u'Auto', video.ressort)
        self.assertEquals(True, video.dailyNewsletter)
        self.assertEquals(False, video.breaking_news)
        self.assertEquals(('Politik', 'Deutschland'),
                          video.keywords)
        self.assertRaises(AttributeError, lambda: video.product_id)

    def test_modify(self):
        video = self.repository['video:1234']
        video.subtitle = u'A new subtitle'
        self.assertEquals(u'A new subtitle', video.subtitle)
        # On abort nothing is written to brightcove 
        transaction.abort()
        video = self.repository['video:1234']
        self.assertEquals(
            u'Mehr Glanz, Glamour und erwartungsvolle Spannung',
            video.subtitle)
        # On commit data is written to brightcove
        video.subtitle = u'A new subtitle'
        video.title = u'A new title'
        transaction.commit()
        video = self.repository['video:1234']
        self.assertEquals(1,
                          len(zeit.brightcove.testing.APIConnection.posts))
        self.assertEquals(u'A new subtitle', video.subtitle)

    def test_brightcove_cache_timeout(self):
        # Set the timeout ot 2 seconds
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
