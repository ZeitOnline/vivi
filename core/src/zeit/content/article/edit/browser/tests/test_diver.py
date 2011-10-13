# coding: utf8
# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest2
import zeit.cms.testing
import zeit.content.article.testing


class MemoDiverTest(zeit.content.article.testing.SeleniumTestCase):

    def setUp(self):
        super(MemoDiverTest, self).setUp()
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        self.selenium.waitForElementPresent('id=memo-diver-button')

    def test_diver_should_be_invisible_on_form_load(self):
        s = self.selenium
        s.waitForElementPresent('id=memo-diver')
        s.assertNotVisible('xpath=//div[@id="memo-diver"]')

    def test_diver_button_should_make_diver_visible_and_invisible(self):
        s = self.selenium
        s.waitForElementPresent('id=memo-diver')
        s.assertNotVisible('xpath=//div[@id="memo-diver"]')
        s.click('//span[@id="memo-diver-button"]')
        s.waitForVisible('xpath=//div[@id="memo-diver"]')
        s.click('//span[@id="memo-diver-button"]')
        s.waitForNotVisible('xpath=//div[@id="memo-diver"]')

    def test_form_should_save_entered_memo_on_blur(self):
        s = self.selenium
        s.waitForElementPresent('id=memo-diver')
        s.assertValue('id=memo-diver.memo', '')
        s.type('id=memo-diver.memo', 'Do not publish this article, yet.')
        s.fireEvent('id=memo-diver.memo', 'blur')
        s.waitForElementNotPresent('css=.dirty')
        s.assertValue('id=memo-diver.memo', 'Do not publish this article, yet.')
        s.open(s.getLocation())
        s.waitForElementPresent('id=memo-diver')
        s.assertValue('id=memo-diver.memo', 'Do not publish this article, yet.')


# FIXME: Move this to zeit.edit as soon as a selenium layer is set up properly!!
class OptionsDiverTest(zeit.content.article.testing.SeleniumTestCase):

    def setUp(self):
        super(OptionsDiverTest, self).setUp()
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        self.selenium.waitForElementPresent('id=options-diver-button')

    def test_checkbox_should_exist_for_each_foldable_area(self):
        s = self.selenium
        s.waitForElementPresent('xpath=//div[@class="edit-bar"]')
        foldables = s.selenium.get_xpath_count('//div[@class="edit-bar"]')
        s.assertXpathCount('//input[@class="fold-checker"]', foldables);
        s.assertText(
            'xpath=//input[@name="edit-form-metadata"]/following-sibling::label',
            'Metadata')
        s.assertChecked('xpath=//input[@name="edit-form-metadata"]')

    def test_unchecked_area_should_be_folded_after_reload(self):
        s = self.selenium
        s.assertNotAttribute('css=#edit-form-metadata@class', 'folded')
        s.waitForElementPresent('id=edit-form-metadata')
        s.click('//div[@id="options-diver"]//input[@name="edit-form-metadata"]')
        s.assertNotChecked('xpath=//input[@name="edit-form-metadata"]')
        s.open(s.getLocation())
        s.waitForElementPresent('css=#edit-form-metadata.folded')
