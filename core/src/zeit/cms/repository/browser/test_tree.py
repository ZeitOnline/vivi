# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.selenium


class Test(zeit.cms.selenium.Test):

    def test_tree_keeps_state(self):
        s = self.selenium

        s.comment(
            "Delete the tree state cookie to have a defined starting point")
        s.deleteCookie('zeit.cms.repository.treeState', '/')
        self.open('/')
        s.verifyTextPresent('online')

        s.comment("Open `online`")
        s.click('//li[@uniqueid="http://xml.zeit.de/online"]')
        s.waitForElementPresent(
            '//li[@uniqueid="http://xml.zeit.de/online/2007"]')

        s.comment("Tree is still open after reload.")
        self.open('/')
        s.verifyElementPresent(
            '//li[@uniqueid="http://xml.zeit.de/online/2007"]')
