# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zc.selenium.pytest


class Test(zc.selenium.pytest.Test):

    def test_tree_keeps_state(self):
        s = self.selenium

        s.comment(
            "Delete the tree state cookie to have a defined starting point")
        s.deleteCookie('zeit.cms.repository.treeState', '/')
        s.open('http://%s/++skin++cms/' % (s.server, ))
        s.assertTextPresent('online')

        s.comment("Open `online`")
        s.click('xpath=//span[text() = "online"]/../../img')
        s.waitForTextPresent('2005')

        s.comment('Click on 2005 and make sure we still have the tree open')
        s.clickAndWait('xpath=//span[text() = "2005"]')
        s.assertTextPresent('2005')
