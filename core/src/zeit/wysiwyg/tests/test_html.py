from six import StringIO
from zeit.wysiwyg.testing import VIDEO1, VIDEO2, VIDEO3, PLAYLIST
import lxml.etree
import zeit.cms.testcontenttype.testcontenttype
import zeit.wysiwyg.html
import zeit.wysiwyg.testing


class VideoExpiresTest(zeit.wysiwyg.testing.FunctionalTestCase):

    def setUp(self):
        super().setUp()
        self.step = zeit.wysiwyg.html.VideoStep(None, None)
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


class VideoStepTest(zeit.wysiwyg.testing.FunctionalTestCase):

    def test_empty_hrefs_should_not_break_conversion(self):
        source = """\
<article>
  <body>
    <video href2="" href="" expires="2011-01-03T06:00:00+01:00" format="large"/>
  </body>
</article>
"""
        article = zeit.cms.testcontenttype.testcontenttype.ExampleContentType(
            xml_source=StringIO(source))
        converter = zeit.wysiwyg.html.HTMLConverter(article)
        converter.from_html(
            article.xml['body'],
            """\
<div class="inline-element video">
  <div class="videoId"></div>
  <div class="videoId2"></div>
  <div class="expires">2011-01-03 06:00</div>
  <div class="format">large</div>
</div>
""")
        self.assertEqual(
            {'href': '', 'href2': '',
             'expires': '2011-01-03T06:00:00+01:00', 'format': 'large'},
            article.xml.body.video.attrib)


class TopLevelTest(zeit.wysiwyg.testing.FunctionalTestCase):

    def test_regression_conversion_to_p_copes_with_non_element_nodes(self):
        source = '<article><body></body></article>'
        article = zeit.cms.testcontenttype.testcontenttype.ExampleContentType(
            xml_source=StringIO(source))
        converter = zeit.wysiwyg.html.HTMLConverter(article)
        converter.from_html(article.xml['body'], '<!-- foo --><p>Foo</p>')
        self.assertEqual(
            '<article><body><!-- foo --><p>Foo</p></body></article>',
            lxml.etree.tostring(article.xml, encoding='unicode'))
