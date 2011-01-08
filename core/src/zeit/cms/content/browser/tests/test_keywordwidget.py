# coding: utf8
# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


class TestKeywordWidget(zeit.cms.testing.SeleniumTestCase):

    def test_lightbox_should_scroll(self):
        s = self.selenium

        self.open('/repository/testcontent')
        s.clickAndWait('link=Checkout*')
        s.click('new_keyword')
        s.waitForElementPresent('css=.keyword-input')
        offset = s.getEval(
            "this.browserbot.findElement('css=.keyword-input').offsetLeft")
        self.assertTrue(offset > 0)
