import zeit.content.cp
import zeit.content.cp.centerpage
import zeit.content.cp.testing


class TestPodcast(zeit.content.cp.testing.BrowserTestCase):

    def setUp(self):
        super(TestPodcast, self).setUp()
        self.centerpage = zeit.content.cp.centerpage.CenterPage()
        self.centerpage['lead'].create_item('podcast')
        self.repository['centerpage'] = self.centerpage
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository/centerpage/@@checkout')
        b.open('contents')
        self.content_url = b.url

    def test_can_create_podcast_module_via_drag_n_drop_from_sidebar(self):
        b = self.browser
        self.assertEqual(1, b.contents.count('type-podcast'))
        b.open('informatives/@@landing-zone-drop-module?block_type=podcast')
        b.open(self.content_url)
        self.assertEqual(2, b.contents.count('type-podcast'))

    def test_podcast_id_is_editable(self):
        b = self.browser
        b.getLink('Edit block properties', index=0).click()
        b.getControl('Podcast id').value = '12345'
        zeit.content.cp.centerpage._test_helper_cp_changed = False
        b.getControl('Apply').click()
        self.assertTrue(zeit.content.cp.centerpage._test_helper_cp_changed)
        self.assertEllipsis('...Updated on...', b.contents)

        b.open(self.content_url)
        self.assertEllipsis('...ID:...12345...', b.contents)
        b.getLink('Edit block properties', index=0).click()
        self.assertEqual('12345', b.getControl('Podcast id').value.strip())
        self.assertEqual(
            ['ZEIT ONLINE'], b.getControl('Provider').displayValue)
