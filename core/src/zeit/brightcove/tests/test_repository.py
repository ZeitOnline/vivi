# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.brightcove.interfaces
import zeit.brightcove.testing
import zope.component


class RepositoryTest(zeit.brightcove.testing.BrightcoveTestCase):

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
