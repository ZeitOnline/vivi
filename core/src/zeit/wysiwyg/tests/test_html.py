# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.wysiwyg.testing import VIDEO1, VIDEO2, PLAYLIST
import zeit.wysiwyg.html
import zeit.wysiwyg.testing
import zope.interface.common.idatetime


class VideoExpiresTest(zeit.wysiwyg.testing.WYSIWYGTestCase):

    def setUp(self):
        super(VideoExpiresTest, self).setUp()
        self.step = zeit.wysiwyg.html.VideoStep(None)
        self.video1 = zeit.cms.interfaces.ICMSContent(VIDEO1)
        self.video2 = zeit.cms.interfaces.ICMSContent(VIDEO2)

    def localize(self, dt):
        tz = zope.interface.common.idatetime.ITZInfo(self.step.request)
        return tz.localize(dt).isoformat()

    def test_user_entered_should_take_preference(self):
        self.assertEqual(
            '2010-07-07 00:00',
            self.step._expires(VIDEO1, VIDEO1, '2010-07-07 00:00'))

    def test_no_user_entry_should_take_expires_from_video(self):
        self.assertEqual(
            self.localize(self.video1.expires),
            self.step._expires(VIDEO1, VIDEO1, None))

    def test_empty_video_id_should_be_ignored(self):
        self.assertEqual(
            self.localize(self.video1.expires),
            self.step._expires(VIDEO1, '', None))

    def test_playlist_should_be_ignored(self):
        self.assertEqual(
            self.localize(self.video1.expires),
            self.step._expires(VIDEO1, PLAYLIST, None))

    def test_two_videos_should_yield_earlier_date(self):
        self.assertEqual(
            self.localize(self.video2.expires),
            self.step._expires(VIDEO1, VIDEO2, None))
