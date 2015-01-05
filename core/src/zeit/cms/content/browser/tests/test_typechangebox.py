# coding: utf8
# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


class TestTypeChangeBox(zeit.cms.testing.ZeitCmsSeleniumTestCase):

    def test_box_should_scroll(self):
        s = self.selenium
        self.open('/repository/online/2007/01/Somalia')
        s.setWindowSize(1000, 300)
        s.click('css=a[title="Additional actions"]')
        s.click('link=Change type')
        s.waitForElementPresent('css=.lightbox-full')
        element = "window.jQuery('.lightbox-full')[0]"
        scroll = s.getEval(element + '.scrollHeight')
        offset = s.getEval(element + '.offsetHeight')
        self.assertGreater(scroll, offset)
