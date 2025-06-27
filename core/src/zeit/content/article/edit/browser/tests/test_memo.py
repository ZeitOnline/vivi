import time

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

    def test_textarea_height_increasing_with_further_text_lines(self):
        s = self.selenium
        s.click('id=memo.memo.preview')
        textarea_height_0 = s.getElementHeight('id=memo.memo')
        multilines = '\n'.join([f'* Line {i + 1}' for i in range(10)])
        s.type('id=memo.memo', multilines)
        textarea_height_1 = s.getElementHeight('id=memo.memo')
        s.type('id=memo.memo', multilines)
        textarea_height_2 = s.getElementHeight('id=memo.memo')
        assert textarea_height_2 > textarea_height_1 > textarea_height_0

    def test_textarea_height_approximately_identical_after_clicking_out_and_in(self):
        s = self.selenium
        s.click('id=memo.memo.preview')
        multilines = '\n'.join([f'* Line {i + 1}' for i in range(10)])
        s.type('id=memo.memo', multilines)
        textarea_height_1 = s.getElementHeight('id=memo.memo')
        s.keyPress('id=memo.memo', Keys.TAB)
        time.sleep(0.5)
        s.click('id=memo.memo.preview')
        assert textarea_height_1 - s.getElementHeight('id=memo.memo') < 5
