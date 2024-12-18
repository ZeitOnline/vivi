from unittest import mock
import contextlib
import unittest

from pendulum import datetime
import lxml.builder

from zeit.content.article.edit.video import Video
import zeit.content.article.edit.tests.test_reference
import zeit.content.article.testing


class VideoTest(unittest.TestCase):
    def get_video(self):
        video = lxml.builder.E.video()
        lxml.builder.E.tree(video)
        video = Video(None, video)
        # Don't validate here. Validation is verified via browser test
        video._validate = mock.Mock()
        return video

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
            self.assertEqual(icc.return_value, video_ob)
            icc.assert_called_with('testid', None)

    def test_unset_video_should_return_none(self):
        video = self.get_video()
        self.assertEqual(None, video.video)

    def test_expires_should_be_set(self):
        video_obj = mock.Mock()
        video_obj.uniqueId = 'vid1'

        def cmscontent(id, default=None):
            if id == 'vid1':
                return video_obj
            return default

        icc = mock.Mock(side_effect=cmscontent)
        video = self.get_video()
        with mock.patch('zeit.cms.interfaces.ICMSContent', new=icc):
            video_obj.expires = datetime(2001, 4, 1, 3, 6)
            video.video = video_obj
            self.assertEqual('2001-04-01T03:06:00+00:00', video.xml.get('expires'))

    def test_layout_should_be_set_to_format_attribute(self):
        video = self.get_video()
        video.layout = 'small'
        self.assertEqual('small', video.layout)
        self.assertEqual('small', video.xml.get('format'))

    def test_layout_should_not_fail_for_invalid_format_attribute(self):
        video = self.get_video()
        video.xml.set('format', 'invalid')
        self.assertEqual('invalid', video.layout)


class TestFactory(zeit.content.article.testing.FunctionalTestCase):
    def test_factory_should_create_video_node(self):
        import zope.component

        import zeit.content.article.article
        import zeit.content.article.edit.interfaces
        import zeit.edit.interfaces

        article = zeit.content.article.article.Article()
        body = zeit.content.article.edit.body.EditableBody(article, article.xml.find('body'))
        factory = zope.component.getAdapter(body, zeit.edit.interfaces.IElementFactory, 'video')
        self.assertEqual('Video', factory.title)
        div = factory()
        self.assertTrue(zeit.content.article.edit.interfaces.IVideo.providedBy(div))
        self.assertEqual('video', div.xml.tag)


class VideoUpdateTest(zeit.content.article.testing.FunctionalTestCase):
    @contextlib.contextmanager
    def video_block(self):
        import zope.component

        import zeit.cms.checkout.helper
        import zeit.content.article.edit.body
        import zeit.edit.interfaces

        self.repository['article'] = self.get_article()
        with zeit.cms.checkout.helper.checked_out(self.repository['article']) as article:
            body = zeit.content.article.edit.body.EditableBody(article, article.xml.find('body'))
            factory = zope.component.getAdapter(body, zeit.edit.interfaces.IElementFactory, 'video')
            video = factory()
            yield video

    def test_expires_is_updated_on_checkin(self):
        from zeit.content.video.video import Video

        self.repository['video'] = Video()
        with zeit.cms.checkout.helper.checked_out(self.repository['video']) as co:
            co.expires = datetime(2012, 1, 1)

        with self.video_block() as block:
            block.video = self.repository['video']
        article = self.repository['article']
        self.assertEqual(
            '2012-01-01T00:00:00+00:00', article.xml.find('body/division/video').get('expires')
        )


class VideoEmptyMarker(
    zeit.content.article.testing.FunctionalTestCase,
    zeit.content.article.edit.tests.test_reference.EmptyMarkerTest,
):
    block_type = 'video'

    def create_target(self):
        from zeit.content.video.video import Video

        self.repository['video'] = Video()
        return self.repository['video']

    def set_reference(self, block, target):
        block.video = target
