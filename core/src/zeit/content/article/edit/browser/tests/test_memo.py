from selenium.webdriver.common.keys import Keys
import zeit.content.article.testing


class Memo(zeit.content.article.testing.SeleniumTestCase):
    def setUp(self):
        super().setUp()
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        self.selenium.waitForElementPresent('id=memo.memo')

    def test_links_are_clickable(self):
        s = self.selenium
        s.click('id=memo.memo.preview')
        s.type('id=memo.memo', 'foo http://localhost/blub bar')
        s.keyPress('id=memo.memo', Keys.TAB)
        s.waitForElementPresent('link=*blub*')
        s.clickAndWait('link=*blub*')
        s.selectWindow(s.getAllWindowIds()[-1])
        s.waitForLocation('*blub')
