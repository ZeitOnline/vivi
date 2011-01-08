# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


class TestClipboard(zeit.cms.testing.SeleniumTestCase):

    def test_adding_via_drag_and_drop(self):
        self.open('/repository')
        s = self.selenium

        # First, we need to fill the clipboard.
        # Creat clip
        s.click('id=clip-add-folder-link')
        s.type('id=clip-add-folder-title', 'Clip')
        s.click('id=clip-add-folder-submit')
        s.waitForElementPresent('link=Clip')
        # Open clip
        s.click('//li[@uniqueid="Clip"]')
        s.waitForElementPresent('//li[@uniqueid="Clip"][@action="collapse"]')

        s.click('xpath=//td[contains(string(.), "testcontent")]')
        s.waitForElementPresent('css=div#bottomcontent > div')
        s.pause(500)
        s.dragAndDropToObject(
            'xpath=//td[contains(string(.), "testcontent")]',
            '//li[@uniqueid="Clip"]')
        s.pause(500)
