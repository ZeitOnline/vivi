import zeit.cms.testing
import zeit.content.cp
import zeit.content.cp.centerpage


class TestHeaderImage(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.ZCML_LAYER

    def setUp(self):
        super(TestHeaderImage, self).setUp()
        with zeit.cms.testing.site(self.getRootFolder()):
            self.centerpage = zeit.content.cp.centerpage.CenterPage()
            self.centerpage['lead'].create_item('headerimage')
            self.repository['centerpage'] = self.centerpage
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository/centerpage/@@checkout')
        b.open('contents')
        self.content_url = b.url
        self.xml_url = 'http://localhost/++skin++vivi/workingcopy/zope.user/' \
            'centerpage/@@xml_source_edit.html'


    def test_can_create_headerimage_module_via_drag_n_drop_from_sidebar(self):
        b = self.browser
        self.assertEqual(1, b.contents.count('type-headerimage'))
        b.open('informatives/@@landing-zone-drop-module?block_type=headerimage')
        b.open(self.content_url)
        self.assertEqual(2, b.contents.count('type-headerimage'))
