# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


class TestMenu(zeit.cms.testing.SeleniumTestCase):

    def test_double_click_activates_once(self):
        s = self.selenium

        self.open('/repository/online/2007/01/Somalia')
        s.click('link=Checkout*')
        s.clickAndWait('link=Checkout*')
        s.verifyTextPresent('checked out')
