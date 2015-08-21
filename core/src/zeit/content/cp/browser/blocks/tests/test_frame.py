import zeit.cms.testing
import zeit.content.cp
import zeit.content.cp.centerpage


class TestFrame(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.ZCML_LAYER

    def setUp(self):
        super(TestFrame, self).setUp()
        with zeit.cms.testing.site(self.getRootFolder()):
            self.centerpage = zeit.content.cp.centerpage.CenterPage()
            self.centerpage['lead'].create_item('frame')
            self.repository['centerpage'] = self.centerpage
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository/centerpage/@@checkout')
        b.open('contents')
        self.content_url = b.url

    def test_can_create_frame_module_via_drag_n_drop_from_sidebar(self):
        b = self.browser
        self.assertEqual(1, b.contents.count('type-frame'))
        b.open('informatives/@@landing-zone-drop-module?block_type=frame')
        b.open(self.content_url)
        self.assertEqual(2, b.contents.count('type-frame'))

    def test_setting_url_validates_it(self):
        b = self.browser

        b.getLink('Edit block properties', index=0).click()
        b.getControl('URL to include').value = 'foo/bar'
        b.getControl('Apply').click()
        self.assertEllipsis('...The specified URI is not valid...', b.contents)
        b.getControl('URL to include').value = 'feed://foo'
        b.getControl('Apply').click()
        self.assertEllipsis(
            '...Only http and https are supported...', b.contents)

        b.getControl('URL to include').value = 'http://example.com/foo'
        zeit.content.cp.centerpage._test_helper_cp_changed = False
        b.getControl('Apply').click()
        self.assertTrue(zeit.content.cp.centerpage._test_helper_cp_changed)
        self.assertEllipsis('...Updated on...', b.contents)

        b.open(self.content_url)
        self.assertEllipsis('...http://example.com/foo...', b.contents)
        b.getLink('Edit block properties', index=0).click()
        self.assertEqual('http://example.com/foo', b.getControl('URL').value)
