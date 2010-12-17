# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.article.testing


class WorkflowStatusTest(zeit.content.article.testing.SeleniumTestCase):

    layer = zeit.content.article.testing.selenium_workflow_layer

    def setUp(self):
        super(WorkflowStatusTest, self).setUp()
        self.open('/repository/online/2007/01/Somalia/')
        self.open('/repository/online/2007/01/Somalia/@@edit.html')
        self.selenium.waitForElementPresent('id=workflow-status.edited')

    def test_status_should_be_select_box(self):
        s = self.selenium
        self.assertEqual([u'no', u'yes', u'not necessary'],
                         s.getSelectOptions('id=workflow-status.edited'))

    def test_status_should_be_settable(self):
        s = self.selenium
        s.select('id=workflow-status.edited', 'label=yes')
        s.fireEvent('id=workflow-status.edited', 'blur')
        s.waitForElementNotPresent('css=.dirty')
        s.open(s.getLocation())
        # Log is being updated:
        self.selenium.waitForTextPresent('status-edited: yes')

    def test_status_should_not_be_editable_in_checkout(self):
        s = self.selenium
        s.clickAndWait('link=Checkout*')
        # No value has been set, yet
        self.assert_widget_text('workflow-status.edited', 'Nothing')


class WorkflowSettingsTest(zeit.content.article.testing.SeleniumTestCase):

    layer = zeit.content.article.testing.selenium_workflow_layer

    def setUp(self):
        super(WorkflowSettingsTest, self).setUp()
        self.open('/repository/online/2007/01/Somalia/')
        self.open('/repository/online/2007/01/Somalia/@@edit.html')
        self.selenium.waitForElementPresent(
            'id=worfklow-settings.release_period.combination_00')

    def test_calendar_should_insert_date(self):
        s = self.selenium
        s.click('id=worfklow-settings.release_period.combination_00_trigger')
        s.waitForElementPresent('css=.calendar')
        s.mouseDown('css=.calendar .button:contains(Today)')
        s.mouseUp('css=.calendar .button:contains(Today)')
        s.waitForElementPresent('css=.dirty')
        s.fireEvent('id=worfklow-settings.release_period.combination_00',
                    'blur')
        s.waitForElementNotPresent('css=.dirty')

    def test_week_button_should_insert_date(self):
        s = self.selenium
        s.click(
            'xpath='
            '//*[@id="worfklow-settings.release_period.combination_00_trigger"]'
            '/following-sibling::input')
        s.waitForElementPresent('css=.dirty')
        s.fireEvent('id=worfklow-settings.release_period.combination_00',
                    'blur')
        s.waitForElementNotPresent('css=.dirty')
