# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.selenium


class TestPanels(zeit.cms.selenium.Test):

    def test_tablelisting_filter(self):
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
