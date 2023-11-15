import zeit.content.cp
import zeit.content.cp.centerpage


class TestCardstack(zeit.content.cp.testing.BrowserTestCase):
    def test_cardstack_props_can_be_set(self):
        self.centerpage = zeit.content.cp.centerpage.CenterPage()
        self.centerpage['lead'].create_item('cardstack')
        self.repository['centerpage'] = self.centerpage
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/centerpage/@@checkout')
        b.open('contents')
        b.getLink('Edit block properties', index=0).click()
        form_url = b.url
        b.getControl('Cardstack id').value = '123'
        b.getControl('Background color').displayValue = ['#D8D8D8']
        b.getControl('Apply').click()
        b.open(form_url)
        self.assertFalse('There were errors' in b.contents)
        self.assertEqual('123', b.getControl('Cardstack id').value)
        self.assertEqual(['#D8D8D8'], b.getControl('Background color').displayValue)
