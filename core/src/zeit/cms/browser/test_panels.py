# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zc.selenium.pytest


class Test(zc.selenium.pytest.Test):

    def test_tablelisting_filter(self):
        s = self.selenium

        s.comment("Open a folder with articles.")
        s.open('http://%s/++skin++cms/repository/online/2007/01' %(s.server, ))

        self.assertPanelState('NavtreePanel', 'unfolded') 
        s.click('//div[@id = "NavtreePanel"]/h1/a')
        self.assertPanelState('NavtreePanel', 'folded') 
        

    def assertPanelState(self, id, state):
        s = self.selenium
        s.assertElementPresent("//div[@id ='%s'][@class = '%s']" %(id, state))
