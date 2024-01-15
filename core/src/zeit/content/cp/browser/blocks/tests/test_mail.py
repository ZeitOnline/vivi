import zeit.content.cp
import zeit.content.cp.centerpage
import zeit.content.cp.testing


class TestMail(zeit.content.cp.testing.BrowserTestCase):
    def setUp(self):
        super().setUp()
        self.centerpage = zeit.content.cp.centerpage.CenterPage()
        self.centerpage.body['lead'].create_item('mail')
        self.repository['centerpage'] = self.centerpage
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/centerpage/@@checkout')
        b.open('contents')
        self.content_url = b.url

    def test_can_create_mail_module_via_drag_n_drop_from_sidebar(self):
        b = self.browser
        self.assertEqual(1, b.contents.count('type-mail'))
        b.open('body/informatives/@@landing-zone-drop-module?block_type=mail')
        b.open(self.content_url)
        self.assertEqual(2, b.contents.count('type-mail'))

    def test_mail_id_is_editable(self):
        b = self.browser
        b.handleErrors = False
        b.getLink('Edit block properties', index=0).click()
        b.getControl('Recipient').value = 'test@localhost'
        b.getControl('Subject').displayValue = ['Apps']
        b.getControl('Success message').value = 'thankyou'
        zeit.content.cp.centerpage._test_helper_cp_changed = False
        b.getControl('Apply').click()
        self.assertTrue(zeit.content.cp.centerpage._test_helper_cp_changed)
        self.assertEllipsis('...Updated on...', b.contents)

        b.open(self.content_url)
        self.assertEllipsis('...Subject:...Apps...', b.contents)
        b.getLink('Edit block properties', index=0).click()
        self.assertEqual('test@localhost', b.getControl('Recipient').value)
        self.assertEqual(['Apps'], b.getControl('Subject').displayValue)
        self.assertEqual('thankyou', b.getControl('Success message').value)
