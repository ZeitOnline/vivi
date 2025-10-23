from unittest import mock
import unittest

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
        video.references = video_obj
        self.assertEqual(video_obj.uniqueId, video.xml.get('href'))

    def test_setting_none_video_should_remove_href(self):
        video = self.get_video()
        video.xml.set('href', 'testid')
        video.references = None
        self.assertFalse('href' in video.xml.attrib)
        # Removing again doesn't fail
        video.references = None

    def test_unset_video_should_return_none(self):
        video = self.get_video()
        self.assertEqual(None, video.references)

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


class VideoEmptyMarker(
    zeit.content.article.testing.FunctionalTestCase,
    zeit.content.article.edit.tests.test_reference.EmptyMarkerTest,
):
    block_type = 'video'

    def create_target(self):
        from zeit.content.video.video import Video

        self.repository['video'] = Video()
        return self.repository['video']
