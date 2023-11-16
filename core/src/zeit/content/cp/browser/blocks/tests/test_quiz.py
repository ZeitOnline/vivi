import zeit.content.cp
import zeit.content.cp.centerpage


class TestQuiz(zeit.content.cp.testing.BrowserTestCase):
    def setUp(self):
        super().setUp()
        self.centerpage = zeit.content.cp.centerpage.CenterPage()
        self.centerpage['lead'].create_item('quiz')
        self.repository['centerpage'] = self.centerpage
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/centerpage/@@checkout')
        b.open('contents')
        self.content_url = b.url

    def test_can_create_quiz_module_via_drag_n_drop_from_sidebar(self):
        b = self.browser
        self.assertEqual(1, b.contents.count('type-quiz'))
        b.open('informatives/@@landing-zone-drop-module?block_type=quiz')
        b.open(self.content_url)
        self.assertEqual(2, b.contents.count('type-quiz'))

    def test_quiz_id_is_editable(self):
        b = self.browser
        b.getLink('Edit block properties', index=0).click()
        b.getControl('Quiz id').value = '12345'
        zeit.content.cp.centerpage._test_helper_cp_changed = False
        b.getControl('Apply').click()
        self.assertTrue(zeit.content.cp.centerpage._test_helper_cp_changed)
        self.assertEllipsis('...Updated on...', b.contents)

        b.open(self.content_url)
        self.assertEllipsis('...ID:...12345...', b.contents)
        b.getLink('Edit block properties', index=0).click()
        self.assertEqual('12345', b.getControl('Quiz id').value.strip())
