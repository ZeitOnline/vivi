# coding: utf8
# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest2
import zeit.content.article.testing


class WorkflowLogTest(zeit.content.article.testing.SeleniumTestCase):

    def setUp(self):
        super(WorkflowLogTest, self).setUp()
        self.open('/repository/online/2007/01/Somalia/')
        self.open('/repository/online/2007/01/Somalia/@@edit.html')
        self.selenium.waitForElementPresent('id=edit-form-workflow')

    def test_expander_should_be_visible_after_five_log_entries(self):
        s = self.selenium
        s.waitForElementPresent('id=urgent.urgent')
        s.assertElementNotPresent('xpath=//button[@class="log-expander"]')

        # Send loggable actions five times.
        for i in range(5):
            s.click('id=urgent.urgent')
            s.fireEvent('id=urgent.urgent', 'blur')
            s.waitForElementNotPresent('css=.dirty')
        s.refresh()
        s.waitForElementPresent('id=urgent.urgent')

        # The expander is still invisible.
        s.assertElementNotPresent('xpath=//button[@class="log-expander"]')

        # With the sixth log entry it will show up.
        s.click('id=urgent.urgent')
        s.fireEvent('id=urgent.urgent', 'blur')
        s.waitForElementNotPresent('css=.dirty')
        s.refresh()
        s.waitForElementPresent('id=urgent.urgent')
        s.assertElementPresent('xpath=//button[@class="log-expander"]')

    def test_expander_should_be_expandable(self):
        s = self.selenium
        s.waitForElementPresent('id=urgent.urgent')
        s.assertElementNotPresent('xpath=//button[@class="log-expander"]')
        for i in range(6):
            s.click('id=urgent.urgent')
            s.fireEvent('id=urgent.urgent', 'blur')
            s.waitForElementNotPresent('css=.dirty')
        s.refresh()
        s.waitForElementPresent('id=urgent.urgent')
        s.assertAttribute(
            'xpath=//fieldset[@class="workflow-log"]//div[@class="widget-outer"]@style',
            '*max-height: 7.5em;*')
        s.assertAttribute(
            'xpath=//fieldset[@class="workflow-log"]//div[@class="widget-outer"]@style',
            '*overflow: hidden;*')
        s.click('xpath=//button[@class="log-expander"]')
        s.assertAttribute(
            'xpath=//fieldset[@class="workflow-log"]//div[@class="widget-outer"]@style',
            'overflow: hidden;')
        s.click('xpath=//button[@class="log-expander"]')
        s.assertAttribute(
            'xpath=//fieldset[@class="workflow-log"]//div[@class="widget-outer"]@style',
            '*max-height: 7.5em;*')
        s.assertAttribute(
            'xpath=//fieldset[@class="workflow-log"]//div[@class="widget-outer"]@style',
            '*overflow: hidden;*')
