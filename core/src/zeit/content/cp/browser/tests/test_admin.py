from zeit.content.cp.centerpage import CenterPage
import zeit.content.cp.testing


class TestAdminMenu(zeit.content.cp.testing.BrowserTestCase):
    login_as = 'zmgr:mgrpw'

    def test_smoke(self):
        self.repository['centerpage'] = CenterPage()

        b = self.browser
        b.open('http://localhost/++skin++vivi' '/repository/centerpage/@@admin.html')
        with self.assertNothingRaised():
            b.getControl('Adjust last published')
        b.getLink('Checkout').click()
        b.getLink('Admin').click()
        with self.assertNothingRaised():
            b.getControl('Banner', index=1)
