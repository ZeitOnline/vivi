# coding: utf8
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.selenium


class TestTabs(zeit.cms.selenium.Test):

    def setUp(self):
        super(TestTabs, self).setUp()
        self.open('/find')
        self.selenium.waitForVisible('id=fulltext')

    def assertSelected(self, href):
        self.selenium.verifyElementPresent(
            '//li[@class="selected"]/a[@href="%s"]' % href)

    def test_on_startup_search_should_be_active(self):
        self.assertSelected('search_form')

    def test_activate_favorites(self):
        s = self.selenium
        s.click('link=Favoriten')
        s.waitForVisible('id=favorites')
        self.assertSelected('favorites')
