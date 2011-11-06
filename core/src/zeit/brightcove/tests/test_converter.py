# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.brightcove.converter import Video, Playlist
import datetime
import mock
import pytz
import transaction
import unittest2 as unittest  # XXX
import zeit.brightcove.converter
import zeit.brightcove.testing
import zeit.cms.browser.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.relation.interfaces
import zeit.cms.testing
import zeit.cms.workflow.interfaces
import zeit.content.video.video
import zope.component
import zope.publisher.browser


class VideoTest(zeit.brightcove.testing.BrightcoveTestCase):

    def test_basic_properties_are_converted_to_cms_names(self):
        video = Video.find_by_id('1234')
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

    def test_keywords(self):
        whitelist = zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)
        whitelist['Politik'] = self.get_tag('Politik')
        video = Video.find_by_id('1234')
        self.assertEquals(['Politik'], [kw.code for kw in video.keywords])
        video.keywords = (self.get_tag('staatsanwaltschaft'),
                          self.get_tag('parlament'))
        self.assertEquals('staatsanwaltschaft;parlament',
                          video.data['customFields']['cmskeywords'])

    def test_bool(self):
        video = Video.find_by_id('1234')
        self.assertEquals(True, video.dailyNewsletter)
        video.dailyNewsletter = False
        self.assertEquals('0',
                          video.data['customFields']['newsletter'])
        video.dailyNewsletter = True
        self.assertEquals('1',
                          video.data['customFields']['newsletter'])

    def test_expires(self):
        video = Video.find_by_id('1234')
        date = datetime.datetime(2010, 3, 26, 5, 0)
        date = pytz.utc.localize(date)
        self.assertEquals(date, video.expires)

    def test_created(self):
        video = Video.find_by_id('1234')
        date = datetime.datetime(2010, 3, 8, 3, 15, 38)
        date = pytz.utc.localize(date)
        self.assertEquals(date, video.date_created)

    def test_released(self):
        video = Video.find_by_id('1234')
        date = datetime.datetime(2010, 3, 8, 12, 59, 57)
        date = pytz.utc.localize(date)
        self.assertEquals(date, video.date_first_released)

    def test_modified(self):
        video = Video.find_by_id('1234')
        date = datetime.datetime(2010, 3, 8, 12, 59, 57)
        date = pytz.utc.localize(date)
        self.assertEquals(date, video.date_first_released)

    def test_videostill(self):
        video = Video.find_by_id('1234')
        self.assertEquals("http://videostillurl", video.video_still)

    def test_thumbnail(self):
        video = Video.find_by_id('1234')
        self.assertEquals("http://thumbnailurl", video.thumbnail)


class VideoConverterTest(zeit.brightcove.testing.BrightcoveTestCase):

    def test_can_be_converted_to_cmscontent(self):
        video = Video.find_by_id('1234')
        cmsobj = video.to_cms()
        self.assertEquals(
            u'Starrummel auf dem Roten Teppich zur 82. Oscar-Verleihung',
            cmsobj.title)
        self.assertTrue(zeit.cms.interfaces.ICMSContent.providedBy(cmsobj))

    def test_unique_id_is_not_copied(self):
        # The unique id will be assigned by the repository. Assigning it
        # ourselves will create confusion and delay.
        video = Video.find_by_id('1234')
        cmsobj = video.to_cms()
        self.assertIsNone(cmsobj.uniqueId)

    def test_brightcove_id_should_be_stored_on_video_in_dav(self):
        video = Video.find_by_id('1234')
        self.assertEqual('1234', video.to_cms().brightcove_id)

    def test_videos_should_be_adaptable_to_ISemanticChange(self):
        metadata = zeit.cms.content.interfaces.ISemanticChange(
            Video.find_by_id('1234').to_cms())
        date = datetime.datetime(2010, 3, 8, 12, 59, 57, tzinfo=pytz.UTC)
        self.assertEqual(date, metadata.last_semantic_change)

    def test_ISemanticChange_should_be_converted_to_brightcove(self):
        cmsobj = zeit.content.video.video.Video()
        sc = zeit.cms.content.interfaces.ISemanticChange(cmsobj)
        date = datetime.datetime(2010, 3, 8, 12, 59, 57, tzinfo=pytz.UTC)
        sc.last_semantic_change = date
        self.assertEqual(date, Video.from_cms(cmsobj).date_last_modified)

    def test_publish_date_is_transferred_to_cms(self):
        info = zeit.cms.workflow.interfaces.IPublishInfo(
            Video.find_by_id('1234').to_cms())
        date = datetime.datetime(2010, 3, 8, 12, 59, 57, tzinfo=pytz.UTC)
        self.assertEqual(date, info.date_last_published)

    def test_publish_date_is_not_transferred_from_cms(self):
        bcobj = Video.find_by_id('1234')
        first_released = bcobj.date_first_released
        cmsobj = bcobj.to_cms()
        info = zeit.cms.workflow.interfaces.IPublishInfo(cmsobj)
        date = datetime.datetime(2011, 3, 9, 14, 59, 57, tzinfo=pytz.UTC)
        info.date_last_published = date
        self.assertEqual(
            first_released, Video.from_cms(cmsobj).date_first_released)

    def test_subtitle_can_contain_unqouted_amp(self):
        video = Video.find_by_id('1234')
        video.subtitle = u'Foo & Bar'
        cms = video.to_cms()
        self.assertEqual(u'Foo &amp; Bar', cms.subtitle)

    def test_too_long_teasertext_should_be_saved(self):
        video = Video.find_by_id('1234')
        too_long = 200 * u'x'
        video.teaserText = too_long
        cms = video.to_cms()
        self.assertEqual(too_long, cms.teaserText)


class PlaylistTest(zeit.brightcove.testing.BrightcoveTestCase):

    def test_basic_properties_are_converted_to_cms_names(self):
        playlist = Playlist.find_by_id('2345')
        self.assertEquals(2345, playlist.id)
        self.assertEquals(u'Videos zum Thema Film', playlist.title)
        self.assertEquals(u'Videos in kurz', playlist.teaserText)

    def test_can_be_converted_to_cmscontent(self):
        playlist = Playlist.find_by_id('2345')
        cmsobj = playlist.to_cms()
        self.assertEquals(u'Videos zum Thema Film', cmsobj.title)
        self.assertTrue(zeit.cms.interfaces.ICMSContent.providedBy(cmsobj))

    def test_videos(self):
        pls = Playlist.find_by_id('2345')
        vids = ('http://xml.zeit.de/video/2010-03/1234',
                'http://xml.zeit.de/video/2010-03/6789')
        self.assertEquals(vids, tuple(v.uniqueId for v in pls.videos))

    def test_videos_should_ignore_lookup_errors(self):
        pls = Playlist.find_by_id('2345')
        pls.data['videoIds'].append(345)
        vids = ('http://xml.zeit.de/video/2010-03/1234',
                'http://xml.zeit.de/video/2010-03/6789')
        self.assertEquals(vids, tuple(v.uniqueId for v in pls.videos))

    def test_title_can_contain_unqouted_amp(self):
        video = Playlist.find_by_id('2345')
        video.title = u'Foo & Bar'
        cms = video.to_cms()
        self.assertEqual(u'Foo &amp; Bar', cms.title)



class TestCheckout(zeit.brightcove.testing.BrightcoveTestCase):

    def test_video_changes_are_written_to_brightcove_on_checkin(self):
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        with zeit.cms.checkout.helper.checked_out(
                video, semantic_change=True) as co:
            co.title = u'local change'
        transaction.commit()
        self.assertEqual(
            1, len(zeit.brightcove.testing.RequestHandler.posts_received))

    def test_video_is_published_on_checkin(self):
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        last_published = zeit.cms.workflow.interfaces.IPublishInfo(
            video).date_last_published
        zeit.cms.workflow.interfaces.IPublish(video).retract()

        with zeit.cms.checkout.helper.checked_out(
                video, semantic_change=True) as co:
            co.title = u'local change'
        transaction.commit()
        zeit.workflow.testing.run_publish()

        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        info = zeit.cms.workflow.interfaces.IPublishInfo(video)
        self.assertTrue(info.published)
        self.assertGreater(info.date_last_published, last_published)

    def test_playlist_changes_are_written_to_brightcove_on_checkin(self):
        playlist = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/playlist/2345')
        last_published = zeit.cms.workflow.interfaces.IPublishInfo(
            playlist).date_last_published
        zeit.cms.workflow.interfaces.IPublish(playlist).retract()

        with zeit.cms.checkout.helper.checked_out(
                playlist, semantic_change=True) as co:
            co.title = u'local change'
        transaction.commit()
        zeit.workflow.testing.run_publish()

        info = zeit.cms.workflow.interfaces.IPublishInfo(playlist)
        self.assertTrue(info.published)
        self.assertGreater(info.date_last_published, last_published)

    def test_playlist_is_updated_on_checkin(self):
        playlist = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/playlist/2345')
        with zeit.cms.checkout.helper.checked_out(
                playlist, semantic_change=True) as co:
            co.title = u'local change'
        transaction.commit()
        self.assertEqual(
            1, len(zeit.brightcove.testing.RequestHandler.posts_received))

    def test_changes_are_written_on_commit(self):
        video = Video.find_by_id('1234')
        video.subtitle = u'A new subtitle'
        video.save()
        transaction.commit()
        self.assertEquals(1, len(self.posts))

    def test_changes_are_not_written_on_abort(self):
        video = Video.find_by_id('1234')
        video.subtitle = u'A new subtitle'
        video.save()
        transaction.abort()
        self.assertEquals(0, len(self.posts))

    def test_brightcove_is_not_updated_by_publication(self):
        video = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2010-03/1234')
        zeit.cms.workflow.interfaces.IPublish(video).publish()
        zeit.workflow.testing.run_publish()
        self.assertEqual(
            0, len(zeit.brightcove.testing.RequestHandler.posts_received))


class TestVideoIdResolver(zeit.cms.testing.FunctionalTestCase):

    def test_video_id_should_be_resolved_to_unique_id(self):
        with mock.patch('zeit.connector.mock.Connector.search') as search:
            search.return_value = iter(
                (('http://xml.zeit.de/video/2010-03/1234',),))
            self.assertEqual(
                u'http://xml.zeit.de/video/2010-03/1234',
                zeit.brightcove.converter.resolve_video_id('1234'))

    def test_should_raise_if_no_object_is_found(self):
        with mock.patch('zeit.connector.mock.Connector.search') as search:
            search.return_value = iter(())
            self.assertRaises(
                LookupError,
                zeit.brightcove.converter.resolve_video_id, '1234')

    def test_should_raise_if_multiple_objects_are_found(self):
        with mock.patch('zeit.connector.mock.Connector.search') as search:
            search.return_value = iter(
                (('http://xml.zeit.de/video/2010-03/1234',),
                 ('http://xml.zeit.de/video/2010-03/1234',),))
            self.assertRaises(
                LookupError,
                zeit.brightcove.converter.resolve_video_id, '1234')


class TestQueryVideoId(unittest.TestCase):

    def test_should_pass_video_to_resolver(self):
        from zeit.brightcove.converter import query_video_id
        with mock.patch('zeit.brightcove.converter.resolve_video_id') as rvi:
            query_video_id(mock.sentinel.avalue)
        rvi.assert_called_with(mock.sentinel.avalue)


    def test_should_return_value(self):
        from zeit.brightcove.converter import query_video_id
        with mock.patch('zeit.brightcove.converter.resolve_video_id') as rvi:
            rvi.return_value = mock.sentinel.result
            self.assertEqual(
                mock.sentinel.result,
                query_video_id(mock.sentinel.avalue))

    def test_should_return_None_on_lookup_error(self):
        from zeit.brightcove.converter import query_video_id
        with mock.patch('zeit.brightcove.converter.resolve_video_id') as rvi:
            rvi.side_effect = LookupError
            self.assertIsNone(
                query_video_id(mock.sentinel.avalue))

    def test_should_return_default_on_lookup_error(self):
        from zeit.brightcove.converter import query_video_id
        with mock.patch('zeit.brightcove.converter.resolve_video_id') as rvi:
            rvi.side_effect = LookupError
            self.assertEqual(
                mock.sentinel.default,
                query_video_id(mock.sentinel.avalue,
                               mock.sentinel.default))


class TestBackwardCompatibleUniqueIds(
    zeit.brightcove.testing.BrightcoveTestCase):

    def test_videos_should_be_resolvable(self):
        from zeit.cms.interfaces import ICMSContent
        expected_unique_id = 'http://xml.zeit.de/testcontent'
        with mock.patch('zeit.brightcove.converter.resolve_video_id') as rvi:
            rvi.return_value = expected_unique_id
            result = ICMSContent('http://video.zeit.de/video/1234')
        self.assertEqual(expected_unique_id, result.uniqueId)
        rvi.assert_called_with('1234')

    def test_playlists_should_be_resolvable(self):
        from zeit.cms.testcontenttype.testcontenttype import TestContentType
        from zeit.cms.interfaces import ICMSContent
        self.repository['video']['playlist']['1234'] = TestContentType()
        expected_unique_id = 'http://xml.zeit.de/video/playlist/1234'
        result = ICMSContent('http://video.zeit.de/playlist/1234')
        self.assertEqual(expected_unique_id, result.uniqueId)
