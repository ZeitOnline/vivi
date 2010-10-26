# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest
import zeit.content.article.testing


class VideoTest(unittest.TestCase):

    def get_video(self):
        from zeit.content.article.edit.video import Video
        import lxml.objectify
        tree = lxml.objectify.E.tree(
            lxml.objectify.E.video())
        return Video(None, tree.video)

    def test_setting_video_should_set_href(self):
        video = self.get_video()
        video_obj = mock.Mock()
        video_obj.uniqueId = 'mock-video-id'
        video_obj.expires = None
        video.video = video_obj
        self.assertEqual(video_obj.uniqueId, video.xml.get('href'))

    def test_setting_none_video_should_remove_href(self):
        video = self.get_video()
        video.xml.set('href', 'testid')
        video.video = None
        self.assertFalse('href' in video.xml.attrib)
        # Removing again doesn't fail
        video.video = None

    def test_set_video_should_be_returned(self):
        video = self.get_video()
        video.xml.set('href', 'testid')
        with mock.patch('zeit.cms.interfaces.ICMSContent') as icc:
            video_ob = video.video
            self.assertEquals(icc.return_value, video_ob)
            icc.assert_called_with('testid', None)

    def test_unset_video_should_return_none(self):
        video = self.get_video()
        self.assertEqual(None, video.video)

    def test_setting_video_2_should_set_href(self):
        video = self.get_video()
        video_obj = mock.Mock()
        video_obj.uniqueId = 'mock-video-id'
        video.video_2 = video_obj
        self.assertEqual(video_obj.uniqueId, video.xml.get('href2'))

    def test_setting_none_video_2_should_remove_href(self):
        video = self.get_video()
        video.xml.set('href2', 'testid')
        video.video_2 = None
        self.assertFalse('href2' in video.xml.attrib)
        # Removing again doesn't fail
        video.video_2 = None

    def test_set_video_2_should_be_returned(self):
        video = self.get_video()
        video.xml.set('href2', 'testid')
        with mock.patch('zeit.cms.interfaces.ICMSContent') as icc:
            video_ob = video.video_2
            self.assertEquals(icc.return_value, video_ob)
            icc.assert_called_with('testid', None)

    def test_unset_video_2_should_return_none(self):
        video = self.get_video()
        self.assertEqual(None, video.video_2)

    def test_expires_should_be_set(self):
        import datetime
        import pytz
        video_obj = mock.Mock()
        video_obj.uniqueId = 'vid1'
        video2_obj = mock.Mock()
        video2_obj.uniqueId = 'vid2'
        def cmscontent(id, default=None):
            if id == 'vid1':
                return video_obj
            if id == 'vid2':
                return video2_obj
            return default
        icc = mock.Mock(side_effect=cmscontent)
        video = self.get_video()
        with mock.patch('zeit.cms.interfaces.ICMSContent', new=icc):
            video_obj.expires = datetime.datetime(
                2001, 4, 1, 3, 6, tzinfo=pytz.UTC)
            video.video = video_obj
            self.assertEqual('2001-04-01T03:06:00+00:00',
                             video.xml.get('expires'))
            video2_obj.expires = datetime.datetime(
                2002, 4, 1, 3, 6, tzinfo=pytz.UTC)
            video.video_2 = video2_obj
            self.assertEqual('2001-04-01T03:06:00+00:00',
                             video.xml.get('expires'))
            video2_obj.expires = datetime.datetime(
                2000, 4, 1, 3, 6, tzinfo=pytz.UTC)
            video.video_2 = video2_obj
            self.assertEqual('2000-04-01T03:06:00+00:00',
                             video.xml.get('expires'))
            video.video_2 = None
            self.assertEqual('2001-04-01T03:06:00+00:00',
                             video.xml.get('expires'))

    def test_layout_should_be_set_to_format_attribute(self):
        video = self.get_video()
        video.layout = u'small'
        self.assertEqual('small', video.layout)
        self.assertEqual('small', video.xml.get('format'))

    def test_layout_should_not_fail_for_invalid_format_attribute(self):
        video = self.get_video()
        video.xml.set('format', 'invalid')
        self.assertEqual('invalid', video.layout)


class TestFactory(zeit.content.article.testing.FunctionalTestCase):

    def test_factory_should_create_video_node(self):
        import zeit.content.article.article
        import zeit.content.article.edit.interfaces
        import zeit.edit.interfaces
        import zope.component
        article = zeit.content.article.article.Article()
        body = zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)
        factory = zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory, 'video')
        self.assertEqual('Video', factory.title)
        div = factory()
        self.assertTrue(
            zeit.content.article.edit.interfaces.IVideo.providedBy(div))
        self.assertEqual('video', div.xml.tag)
