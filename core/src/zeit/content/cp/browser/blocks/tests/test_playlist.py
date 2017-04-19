from zeit.content.video.playlist import Playlist
import urllib2
import zeit.cms.interfaces
import zeit.cms.testing
import zeit.content.cp.interfaces
import zeit.content.cp.testing


class TestPlaylist(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.ZCML_LAYER

    def setUp(self):
        super(TestPlaylist, self).setUp()
        from zeit.content.cp.centerpage import CenterPage
        with zeit.cms.testing.site(self.getRootFolder()):
            self.centerpage = CenterPage()
            self.playlist = self.centerpage['lead'].create_item('playlist')
            self.repository['centerpage'] = self.centerpage
            self.repository['my-playlist'] = Playlist()

        self.browser.open(
            'http://localhost/++skin++vivi/repository/centerpage/@@checkout')
        self.browser.open('contents')
        self.content_url = self.browser.url

    def set_referenced_playlist(self):
        b = self.browser
        b.open(self.content_url)
        b.getLink('Edit block properties', index=0).click()
        b.getControl('Playlist').value = 'http://xml.zeit.de/my-playlist'
        b.getControl('Apply').click()
        b.open(self.content_url)

    def test_can_create_playlist_block_via_drag_n_drop_from_sidebar(self):
        b = self.browser
        self.assertEqual(1, b.contents.count('type-playlist'))
        b.open('informatives/@@landing-zone-drop-module?block_type=playlist')
        b.open(self.content_url)
        self.assertEqual(2, b.contents.count('type-playlist'))

    def test_can_reference_a_playlist_via_drag_n_drop(self):
        [playlist_block] = self.repository['centerpage']['lead'].values()
        drop_url = 'lead/{}/@@drop?uniqueId={}'.format(
            playlist_block.__name__, 'http://xml.zeit.de/my-playlist')

        b = self.browser
        b.open(drop_url)
        b.open(self.content_url)
        b.getLink('Edit block properties', index=0).click()
        self.assertEqual(
            'http://xml.zeit.de/my-playlist', b.getControl('Playlist').value)

    def test_cannot_drop_video(self):
        from zeit.content.video.video import Video
        with zeit.cms.testing.site(self.getRootFolder()):
            self.repository['my-video'] = Video()

        [playlist_block] = self.repository['centerpage']['lead'].values()
        drop_url = 'lead/{}/@@drop?uniqueId={}'.format(
            playlist_block.__name__, 'http://xml.zeit.de/my-video')

        b = self.browser
        with self.assertRaises(urllib2.HTTPError):
            b.open(drop_url)
        self.assertEllipsis(
            '...Only playlists can be dropped on a playlist block...',
            b.contents)

    def test_can_reference_a_playlist_by_editing_common_properties(self):
        self.set_referenced_playlist()
        self.browser.open('@@checkin')
        with zeit.cms.testing.site(self.getRootFolder()):
            [playlist_block] = self.repository['centerpage']['lead'].values()
            self.assertEqual(
                self.repository['my-playlist'],
                playlist_block.referenced_playlist)

    def test_playlist_is_stored_in_xml(self):
        self.set_referenced_playlist()
        self.browser.open('xml_source_edit.html')
        self.assertEllipsis("""...
<container cp:type="playlist"...>
    <block type="intern"
           href="http://xml.zeit.de/my-playlist"
           contenttype="playlist"...>
    ...
    <title xsi:nil="true"/>
    ...
  </block>
</container>...""", self.browser.getControl('XML Source').value)

    def test_playlist_is_part_of_cp_content(self):
        self.set_referenced_playlist()
        self.browser.open('@@checkin')
        with zeit.cms.testing.site(self.getRootFolder()):
            self.assertEqual(
                [self.repository['my-playlist']],
                list(zeit.cms.interfaces.ICMSContentIterable(
                    self.repository['centerpage'])))
