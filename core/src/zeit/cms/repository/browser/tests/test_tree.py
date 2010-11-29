# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


class TestTree(zeit.cms.testing.SeleniumTestCase):

    def test_tree_keeps_state(self):
        s = self.selenium

        # Delete the tree state cookie to have a defined starting point
        s.deleteCookie('zeit.cms.repository.treeState', '/')
        self.open('/', auth='zmgr:mgrpw')
        s.verifyTextPresent('online')

        # Open `online`
        s.click('//li[@uniqueid="http://xml.zeit.de/online"]')
        s.waitForElementPresent(
            '//li[@uniqueid="http://xml.zeit.de/online/2007"]')

        # Tree is still open after reload."
        self.open('/', auth='zmgr:mgrpw')
        s.waitForElementPresent(
            '//li[@uniqueid="http://xml.zeit.de/online/2007"]')
