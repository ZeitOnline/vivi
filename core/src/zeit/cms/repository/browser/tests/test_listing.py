import xml.sax.saxutils

import transaction

from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.testing


class TestListing(zeit.cms.testing.SeleniumTestCase):
    layer = zeit.cms.testing.WEBDRIVER_LAYER
    window_height = 800

    def test_tablelisting_filter(self):
        self.repository['foo'] = ExampleContentType()
        self.repository['bar'] = ExampleContentType()
        transaction.commit()

        s = self.selenium

        # Open a folder with articles.
        self.open('/repository')
        self.verifyTextDisplayed('foo')
        self.verifyTextDisplayed('bar')

        # Type in a word to filter the table
        s.type('name=tableFilter', 'foo')
        self.verifyTextNotDisplayed('bar')
        self.verifyTextDisplayed('foo')

    def test_drag_and_drop_from_table(self):
        # First create a clip to have a target for dragging
        s = self.selenium
        self.open('/repository')
        s.click('id=clip-add-folder-link')
        s.type('id=clip-add-folder-title', 'Clip')
        s.click('id=clip-add-folder-submit')
        s.waitForElementPresent('link=Clip')
        # Open clip
        s.clickAt('//li[@uniqueid="Clip"]', '1,1')
        s.waitForElementPresent('//li[@uniqueid="Clip"][@action="collapse"]')

        # Drag the testcontent to the clipboard
        s = self.selenium
        match = 'testcontent'
        s.click('xpath=//td[contains(string(.), "%s")]' % match)
        s.waitForElementPresent('css=div#bottomcontent > div')
        s.dragAndDropToObject(
            'xpath=//td[contains(string(.), "%s")]' % match, '//li[@uniqueid="Clip"]'
        )
        s.waitForElementPresent('xpath=//li[@uniqueid="Clip/testcontent"]')

    def verifyTextNotDisplayed(self, string):
        self.selenium.verifyNotVisible(
            '//tr[contains(string(.), %s)]' % xml.sax.saxutils.quoteattr(string)
        )

    def verifyTextDisplayed(self, string):
        self.selenium.verifyVisible(
            '//tr[contains(string(.), %s)]' % xml.sax.saxutils.quoteattr(string)
        )
