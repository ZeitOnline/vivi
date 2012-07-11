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
        # XXX type() doesn't work with selenium-1 and FF>7
        self.eval('document.getElementById("memo.memo").value = '
                  '"foo http://localhost/blub bar"')
        s.fireEvent('id=memo.memo', 'blur')
        s.waitForElementPresent('link=*blub*')
        s.click('link=*blub*')
        s.selectWindow(s.getAllWindowNames()[-1])
        s.assertLocation('*blub')
