# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.wysiwyg.testing import VIDEO1, VIDEO2, VIDEO3, PLAYLIST
import zeit.wysiwyg.html
import zeit.wysiwyg.testing


class VideoExpiresTest(zeit.wysiwyg.testing.WYSIWYGTestCase):

    def setUp(self):
        super(VideoExpiresTest, self).setUp()
        self.step = zeit.wysiwyg.html.VideoStep(None)
        self.video1 = zeit.cms.interfaces.ICMSContent(VIDEO1)
        self.video2 = zeit.cms.interfaces.ICMSContent(VIDEO2)

    def test_user_entered_should_take_preference(self):
        self.assertEqual(
            '2010-07-07 00:00',
            self.step._expires(VIDEO1, VIDEO1, '2010-07-07 00:00'))

    def test_no_user_entry_should_take_expires_from_video(self):
        self.assertEqual(
            self.video1.expires.isoformat(),
            self.step._expires(VIDEO1, VIDEO1, None))

    def test_empty_video_id_should_be_ignored(self):
        self.assertEqual(
            self.video1.expires.isoformat(),
            self.step._expires(VIDEO1, '', None))

    def test_playlist_should_be_ignored(self):
        self.assertEqual(
            self.video1.expires.isoformat(),
            self.step._expires(VIDEO1, PLAYLIST, None))

    def test_no_expires_found_should_yield_nothing(self):
        self.assertEqual(
            '', self.step._expires(PLAYLIST, PLAYLIST, None))

    def test_no_expires_date_should_be_ignored(self):
        self.assertEqual(
            '',
            self.step._expires(VIDEO3, PLAYLIST, None))

    def test_two_videos_should_yield_earlier_date(self):
        self.assertEqual(
            self.video2.expires.isoformat(),
            self.step._expires(VIDEO1, VIDEO2, None))
