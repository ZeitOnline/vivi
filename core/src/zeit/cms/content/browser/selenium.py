# coding: utf8
# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.selenium


class TestKeywordWidget(zeit.cms.selenium.Test):

    def test_layout(self):
        s = self.selenium

        self.open('/repository/testcontent')
        s.clickAndWait('link=Checkout*')
        s.click('new_keyword')
        s.waitForElementPresent('css=.keyword-input')
        s.storeEval("this.browserbot.findElement('css=.keyword-input')",
                    'input')
        s.verifyEval("storedVars['input'].offsetLeft > 0", 'true')


class TestTypeChangeBox(zeit.cms.selenium.Test):

    def test_box_scrolls(self):
        s = self.selenium
        self.open('/repository/online/2007/01/Somalia')
        s.click('link=Change type')
        s.waitForElementPresent('css=.lightbox-full')
        s.storeEval("this.browserbot.findElement('css=.lightbox-full')",
                    'contents')
        s.verifyEval("storedVars['contents'].scrollHeight > "
                     "  storedVars['contents'].offsetHeight",
                     'true')
