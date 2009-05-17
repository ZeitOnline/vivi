# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.selenium


class TestPanels(zeit.cms.selenium.Test):

    def test_tree_folding(self):
        s = self.selenium

        s.comment("Open a folder with articles.")
        self.open('/repository/online/2007/01')

        self.assertPanelState('NavtreePanel', 'unfolded')
        s.click('//div[@id = "NavtreePanel"]/h1')
        self.assertPanelState('NavtreePanel', 'folded')
        # Stays that way when reloading
        self.open('/repository/online/2007/01')
        self.assertPanelState('NavtreePanel', 'folded')

        # unfold again:
        s.click('//div[@id = "NavtreePanel"]/h1')
        self.assertPanelState('NavtreePanel', 'unfolded')
        # Stays that way when reloading
        self.open('/repository/online/2007/01')
        self.assertPanelState('NavtreePanel', 'unfolded')

    def assertPanelState(self, id, state):
        s = self.selenium
        s.verifyElementPresent("//div[@id ='%s'][@class = 'panel %s']" %(
            id, state))


class TestMenu(zeit.cms.selenium.Test):

    def test_double_click_activates_once(self):
        s = self.selenium

        self.open('/repository/online/2007/01/Somalia')
        s.click('link=Checkout*')
        s.clickAndWait('link=Checkout*')
        s.verifyTextPresent('checked out')
