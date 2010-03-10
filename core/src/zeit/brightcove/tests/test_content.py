# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import time
import transaction
import zeit.brightcove.interfaces
import zeit.brightcove.testing
import zeit.cms.interfaces
import zope.component


class VideoTest(zeit.brightcove.testing.BrightcoveTestCase):

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.brightcove.interfaces.IRepository)

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
        self.assertTrue(video.product_id is None)

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
        self.assertEquals(1, len(self.posts))
        self.assertEquals(u'A new subtitle', video.subtitle)

    def test_keywords(self):
        video = self.repository['video:1234']
        self.assertEquals(['Politik', 'koalition'],
                          [kw.code for kw in video.keywords])
        keywords = zope.component.getUtility(
            zeit.cms.content.interfaces.IKeywords)
        video.keywords = (keywords['staatsanwaltschaft'],
                          keywords['parlament'])
        self.assertEquals('staatsanwaltschaft;parlament',
                          video.data['customFields']['cmskeywords'])

    def test_bool(self):
        video = self.repository['video:1234']
        self.assertEquals(True, video.dailyNewsletter)
        video.dailyNewsletter = False
        self.assertEquals('0',
                          video.data['customFields']['newsletter'])
        video.dailyNewsletter = True
        self.assertEquals('1',
                          video.data['customFields']['newsletter'])

    def test_related(self):
        video = self.repository['video:1234']
        self.assertEquals((), video.related)
        content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')
        with zeit.cms.checkout.helper.checked_out(content) as co:
            co.teaserTitle = u'a title'
        video.related = (zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent'),)
        self.assertEquals(
            'http://xml.zeit.de/testcontent',
            video.data['customFields']['ref_link1'])
        self.assertEquals(
            'a title',
            video.data['customFields']['ref_title1'])


class PlaylistTest(zeit.brightcove.testing.BrightcoveTestCase):

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.brightcove.interfaces.IRepository)

    def test_getitem(self):
        playlist = self.repository['playlist:2345']
        self.assertTrue(zeit.brightcove.interfaces.IPlaylist.providedBy(playlist))
        self.assertEquals(
            u'Starrummel auf dem Roten Teppich zur 82. Oscar-Verleihung',
            playlist.title)
        self.assertEquals(
            u'Glanz, Glamour und erwartungsvolle Spannung',
            playlist.teaserText)
        self.assertEquals(
            u'Mehr Glanz, Glamour und erwartungsvolle Spannung',
            playlist.subtitle)
        self.assertEquals(u'Auto', playlist.ressort)
        self.assertEquals(True, playlist.dailyNewsletter)
        self.assertEquals(False, playlist.breaking_news)
        self.assertTrue(playlist.product_id is None)
