import zeit.content.article.testing


class TestAdminMenu(zeit.content.article.testing.BrowserTestCase):
    login_as = 'zmgr:mgrpw'

    def test_smoke(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi' '/repository/online/2007/01/Somalia/@@admin.html')
        with self.assertNothingRaised():
            b.getControl('Adjust last published')
        b.getLink('Checkout').click()
        b.getLink('Admin').click()
        with self.assertNothingRaised():
            b.getControl('Has audio file')
