# coding: utf8
# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.article.testing


class Memo(zeit.content.article.testing.SeleniumTestCase):

    def setUp(self):
        super(Memo, self).setUp()
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        self.selenium.waitForElementPresent('id=memo.memo')

    def test_links_are_clickable(self):
        s = self.selenium
        s.click('id=memo.memo.preview')
        s.type('id=memo.memo', 'foo http://localhost/blub bar\t')
        s.waitForElementPresent('link=*blub*')
        s.click('link=*blub*')
        s.selectWindow(s.getAllWindowIds()[-1])
        s.waitForLocation('*blub')
