# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import pytz
import transaction
import zeit.brightcove.interfaces
import zeit.brightcove.testing
import zeit.cms.browser.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.relation.interfaces
import zeit.cms.workflow.interfaces
import zeit.workflow.interfaces
import zope.component
import zope.interface.verify
import zope.publisher.browser


class VideoTest(zeit.brightcove.testing.BrightcoveTestCase):

    def test_cmscontent(self):
        video = self.repository['video-1234']
        self.assertEquals('http://xml.zeit.de/brightcove-folder/video-1234', video.uniqueId)
        self.assertEquals('video-1234', video.__name__)
        self.assertEquals(
            video,
            zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/brightcove-folder/video-1234'))

    def test_getitem(self):
        video = self.repository['video-1234']
        self.assertTrue(zeit.brightcove.interfaces.IVideo.providedBy(video))
        self.assertEquals(1234, video.id)
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
        video = self.repository['video-1234']
        video.subtitle = u'A new subtitle'
        self.assertEquals(u'A new subtitle', video.subtitle)
        # On abort nothing is written to brightcove
        transaction.abort()
        video = self.repository['video-1234']
        self.assertEquals(
            u'Mehr Glanz, Glamour und erwartungsvolle Spannung',
            video.subtitle)
        # On commit data is written to brightcove
        video.subtitle = u'A new subtitle'
        video.title = u'A new title'
        transaction.commit()
        video = self.repository['video-1234']
        self.assertEquals(1, len(self.posts))
        self.assertEquals(u'A new subtitle', video.subtitle)

    def test_keywords(self):
        from zeit.cms.tagging.tag import Tag
        whitelist = zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)
        whitelist['Politik'] = Tag('Politik')
        video = self.repository['video-1234']
        self.assertEquals(['Politik'], [kw.code for kw in video.keywords])
        video.keywords = (Tag('staatsanwaltschaft'), Tag('parlament'))
        self.assertEquals('staatsanwaltschaft;parlament',
                          video.data['customFields']['cmskeywords'])

    def test_bool(self):
        video = self.repository['video-1234']
        self.assertEquals(True, video.dailyNewsletter)
        video.dailyNewsletter = False
        self.assertEquals('0',
                          video.data['customFields']['newsletter'])
        video.dailyNewsletter = True
        self.assertEquals('1',
                          video.data['customFields']['newsletter'])

    def test_related(self):
        video = self.repository['video-1234']
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

    def test_uuid(self):
        # The uuid of videos is the unique id. This works because the unique id
        # contains a database id from brightcove which never changes
        uuid = zeit.cms.content.interfaces.IUUID(self.repository['video-1234'])
        self.assertEquals('http://xml.zeit.de/brightcove-folder/video-1234', uuid.id)

    def test_common_metadata(self):
        metadata = zeit.cms.content.interfaces.ICommonMetadata(
            self.repository['video-1234'])
        self.assertEquals(2010, metadata.year)
        self.assertEquals(
            u'Glanz, Glamour und erwartungsvolle Spannung',
            metadata.teaserText)

    def test_videos_shouild_be_adaptable_to_isemantic_change(self):
        metadata = zeit.cms.content.interfaces.ISemanticChange(
            self.repository['video-1234'])
        date = datetime.datetime(2010, 3, 8, 12, 59, 57)
        date = pytz.utc.localize(date)
        self.assertEquals(date, metadata.last_semantic_change)

    def test_list_repr(self):
        request = zope.publisher.browser.TestRequest(
            skin=zeit.cms.browser.interfaces.ICMSSkin)
        list_repr = zope.component.getMultiAdapter(
            (self.repository['video-1234'], request),
            zeit.cms.browser.interfaces.IListRepresentation)
        self.assertEquals(2010, list_repr.year)
        self.assertEquals(
            'Starrummel auf dem Roten Teppich zur 82. Oscar-Verleihung',
            list_repr.title)

    def test_publication_status(self):
        video = self.repository['video-1234']
        publication_status = zeit.cms.workflow.interfaces.IPublicationStatus(
            video)
        self.assertEquals("published", publication_status.published)
        video.item_state = 'INACTIVE'
        self.assertEquals("not-published", publication_status.published)

    def test_expires(self):
        video = self.repository['video-1234']
        date = datetime.datetime(2010, 3, 26, 5, 0)
        date = pytz.utc.localize(date)
        self.assertEquals(date, video.expires)

    def test_created(self):
        video = self.repository['video-1234']
        date = datetime.datetime(2010, 3, 8, 3, 15, 38)
        date = pytz.utc.localize(date)
        self.assertEquals(date, video.date_created)

    def test_released(self):
        video = self.repository['video-1234']
        date = datetime.datetime(2010, 3, 8, 12, 59, 57)
        date = pytz.utc.localize(date)
        self.assertEquals(date, video.date_first_released)

    def test_modified(self):
        video = self.repository['video-1234']
        date = datetime.datetime(2010, 3, 8, 12, 59, 57)
        date = pytz.utc.localize(date)
        self.assertEquals(date, video.date_first_released)

    def test_videostill(self):
        video = self.repository['video-1234']
        self.assertEquals("http://videostillurl", video.video_still)

    def test_thumbnail(self):
        video = self.repository['video-1234']
        self.assertEquals("http://thumbnailurl", video.thumbnail)

    def test_comment_should_honour_default(self):
        video = self.repository['video-1234']
        self.assertTrue(video.commentsAllowed)


class PlaylistTest(zeit.brightcove.testing.BrightcoveTestCase):

    def test_getitem(self):
        playlist = self.repository['playlist-2345']
        self.assertEquals(2345, playlist.id)
        self.assertTrue(
            zeit.brightcove.interfaces.IPlaylist.providedBy(playlist))
        self.assertEquals(u'Videos zum Thema Film', playlist.title)
        self.assertEquals(u'Videos in kurz', playlist.teaserText)

    def test_cmscontent(self):
        pls = self.repository['playlist-2345']
        self.assertEquals('http://xml.zeit.de/brightcove-folder/playlist-2345', pls.uniqueId)
        self.assertEquals('playlist-2345', pls.__name__)
        self.assertEquals(
            pls,
            zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/brightcove-folder/playlist-2345'))

    def test_publication_status(self):
        video = self.repository['playlist-2345']
        publication_status = zeit.cms.workflow.interfaces.IPublicationStatus(
            video)
        self.assertEquals("published", publication_status.published)

    def test_video_ids(self):
        pls = self.repository['playlist-2345']
        vids = ('http://xml.zeit.de/brightcove-folder/video-1234',
                'http://xml.zeit.de/brightcove-folder/video-6789')
        self.assertEquals(vids, pls.video_ids)

    def test_reference_adapter(self):
        pls = self.repository['playlist-2345']
        vids = zeit.cms.relation.interfaces.IReferences(pls)
        self.assertEquals('http://xml.zeit.de/brightcove-folder/video-1234', vids[0].uniqueId)


class TestPublishInfo(zeit.brightcove.testing.BrightcoveTestCase):

    def test_publishinfo(self):
        video = self.repository['video-1234']
        pi = zeit.cms.workflow.interfaces.IPublishInfo(video)
        zope.interface.verify.verifyObject(
            zeit.cms.workflow.interfaces.IPublishInfo, pi)

    def test_timebased(self):
        video = self.repository['video-1234']
        time = zeit.workflow.interfaces.ITimeBasedPublishing(video)
        zope.interface.verify.verifyObject(
            zeit.workflow.interfaces.ITimeBasedPublishing, time)
