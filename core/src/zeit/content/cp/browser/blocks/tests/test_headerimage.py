import zeit.content.cp
import zeit.content.cp.centerpage


class TestHeaderImage(zeit.content.cp.testing.BrowserTestCase):
    def setUp(self):
        super().setUp()
        self.centerpage = zeit.content.cp.centerpage.CenterPage()
        self.centerpage.body['lead'].create_item('headerimage')
        self.repository['centerpage'] = self.centerpage
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/centerpage/@@checkout')
        b.open('contents')
        self.content_url = b.url
        self.xml_url = (
            'http://localhost/++skin++vivi/workingcopy/zope.user/'
            'centerpage/@@xml_source_edit.html'
        )

    def test_can_create_headerimage_module_via_drag_n_drop_from_sidebar(self):
        b = self.browser
        self.assertEqual(1, b.contents.count('type-headerimage'))
        b.open('body/informatives/@@landing-zone-drop-module?' 'block_type=headerimage')
        b.open(self.content_url)
        self.assertEqual(2, b.contents.count('type-headerimage'))

    def test_headerimage_animate_default_is_set(self):
        b = self.browser
        b.getLink('Edit block properties', index=0).click()
        b.getControl('Image').value = 'http://xml.zeit.de/2006/DSC00109_2.JPG'
        b.getControl('Apply').click()
        b.open(self.xml_url)
        self.assertEllipsis('...animate="False"...', b.contents)

    def test_headerimage_animate_true_is_set(self):
        b = self.browser
        b.getLink('Edit block properties', index=0).click()
        b.getControl('Image').value = 'http://xml.zeit.de/2006/DSC00109_2.JPG'
        b.getControl('Animate').selected = True
        b.getControl('Apply').click()
        b.open(self.content_url)
        b.getLink('Edit block properties', index=0).click()
        assert b.getControl('Animate').selected
