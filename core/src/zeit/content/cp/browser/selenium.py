# coding: utf8
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.selenium


class TestGenericEditing(zeit.cms.selenium.Test):

    def open_centerpage(self):
        s = self.selenium
        self.open('/repository')
        s.selectAndWait('id=add_menu', 'label=CenterPage')
        s.type('form.__name__', 'cp')
        s.type('form.title', 'Deutschland')
        s.type('form.authors.0.', 'Hans Wurst')
        s.select('form.ressort', 'Deutschland')
        s.clickAndWait('id=form.actions.add')
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent('xpath=//div[@class="landing-zone"]')

    def test_insert(self):
        self.open_centerpage()
        s = self.selenium
        s.verifyElementNotPresent('//a[@class="choose-box"]')
        s.click('link=*Add box*')
        s.waitForElementPresent('//a[@class="choose-box"]')
        s.click('//a[@class="choose-box"]')
        s.waitForElementPresent('//div[@class="box-types"]')
        s.click('link=List of teasers')
        s.waitForElementPresent('//div[@class="box type-teaser"]')
        s.click('//div[@class="box type-teaser"]/*/div[@class="edit"]/a')
        s.waitForElementPresent('id=lightbox.form')
        s.type('form.title', 'Holladrio')
        s.click('form.actions.apply')
        s.waitForElementNotPresent('id=lightbox')

        # Open delete verification
        s.pause(0.5)
        s.click('css=a.delete-link')
        s.waitForElementPresent('css=div.confirm-delete')
        s.verifyElementPresent('css=div.box-inner.highlight')

        # Clicking anywhere else but on the remove confirmer, does close the
        # confirm but does not issue any action. Note that we've got to click
        # on the #confirm-delete-overlay which overlays everything.
        s.click("css=#confirm-delete-overlay")
        s.waitForElementNotPresent('css=div.confirm-delete')
        s.verifyElementNotPresent('css=div.box-inner.highlight')

        # Now really delete
        s.click('css=a.delete-link')
        s.click('css=div.confirm-delete > a')
        s.waitForElementNotPresent('css=a.delete-link')

    def test_close_choose_type_lightbox_does_not_break_editor(self):
        self.open_centerpage()
        s = self.selenium
        s.click('link=*Add box*')
        s.waitForElementPresent('css=a.choose-box')
        s.click('//a[@class="choose-box"]')
        s.waitForElementPresent('css=div.box-types')
        s.click('css=a.CloseButton')
        s.waitForElementNotPresent('css=a.CloseButton')

        # The following click used to do nothing. Make sure it does add a box.
        s.click('link=*Add box*')
        s.waitForXpathCount('//a[@class="choose-box"]', 2)


    def test_hover(self):
        self.open_centerpage()
        s = self.selenium

        # Create a box
        s.click('link=*Add box*')
        s.waitForElementPresent('css=a.choose-box')
        s.click('//a[@class="choose-box"]')
        s.waitForElementPresent('css=div.box-types')
        s.click('link=List of teasers')
        s.waitForElementPresent('css=div.type-teaser')

        # Hover mouse over box
        s.verifyElementNotPresent('css=div.box-inner.hover')
        s.mouseOver('css=div.teaser-list')
        s.verifyElementPresent('css=div.box-inner.hover')
        s.mouseOut('css=div.teaser-list')
        s.verifyElementNotPresent('css=div.box-inner.hover')
