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
        s.assertValue('id=memo-diver.memo', 'Do not publish this article, yet.')
        s.open(s.getLocation())
        s.waitForElementPresent('id=memo-diver')
        s.assertValue('id=memo-diver.memo', 'Do not publish this article, yet.')
