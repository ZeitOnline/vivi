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
