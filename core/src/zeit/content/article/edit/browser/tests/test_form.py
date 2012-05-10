# coding: utf-8
# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.content.article.testing


class WorkflowQualityAssuranceTest(
    zeit.content.article.testing.SeleniumTestCase):

    layer = zeit.content.article.testing.selenium_workflow_layer

    def setUp(self):
        super(WorkflowQualityAssuranceTest, self).setUp()
        self.open('/repository/online/2007/01/Somalia/')
        self.open('/repository/online/2007/01/Somalia/@@edit.html')
        self.selenium.waitForElementPresent(
            'id=workflow-quality-assurance.edited')

    def test_status_should_be_select_box(self):
        s = self.selenium
        self.assertEqual(
            [u'no', u'yes', u'not necessary'],
            s.getSelectOptions('id=workflow-quality-assurance.edited'))

    def test_status_should_be_settable(self):
        s = self.selenium
        s.select('id=workflow-quality-assurance.edited', 'label=yes')
        s.fireEvent('id=workflow-quality-assurance.edited', 'blur')
        s.waitForElementNotPresent('css=.dirty')
        s.open(s.getLocation())
        # Log is being updated:
        self.selenium.waitForTextPresent('status-edited: yes')

    def test_status_should_not_be_editable_in_checkout(self):
        s = self.selenium
        s.clickAndWait('link=Checkout*')
        # No value has been set, yet
        self.assert_widget_text('workflow-quality-assurance.edited', 'Nothing')


class WorkflowPublicationPeriodTest(
    zeit.content.article.testing.SeleniumTestCase):

    layer = zeit.content.article.testing.selenium_workflow_layer

    def setUp(self):
        super(WorkflowPublicationPeriodTest, self).setUp()
        self.open('/repository/online/2007/01/Somalia/')
        self.open('/repository/online/2007/01/Somalia/@@edit.html')
        self.selenium.waitForElementPresent(
            'id=workflow-publication-period.release_period.combination_00')

    def test_calendar_should_insert_date(self):
        s = self.selenium
        s.click(
            'id=workflow-publication-period.release_period.combination_00_trigger')
        s.waitForElementPresent('css=.calendar')
        s.mouseDown('css=.calendar .button:contains(Today)')
        s.mouseUp('css=.calendar .button:contains(Today)')
        s.waitForElementPresent('css=.dirty')
        s.fireEvent(
            'id=workflow-publication-period.release_period.combination_00',
            'blur')
        s.waitForElementNotPresent('css=.dirty')

    def test_week_button_should_insert_date(self):
        s = self.selenium
        s.click(
            'xpath='
            '//*[@id="workflow-publication-period.release_period.combination_00_trigger"]'
            '/following-sibling::input')
        s.waitForElementPresent('css=.dirty')
        s.fireEvent(
            'id=workflow-publication-period.release_period.combination_00',
            'blur')
        s.waitForElementNotPresent('css=.dirty')


class CheckinValidationTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.ArticleLayer

    def test_validation_errors_should_be_displayed_at_checkin_button(self):
        from zeit.content.article.article import Article
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                self.repository['article'] = Article()
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/article/@@checkout')
        b.open('@@edit.form.context-action')
        self.assert_ellipsis('...Title:...Required input is missing...')


class MemoTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.ArticleLayer

    def test_memo_is_editable_while_checked_in(self):
        from zeit.content.article.article import Article
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                self.repository['article'] = Article()
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/article/@@edit.form.memo-diver?show_form=1')
        b.getControl('Memo').value = 'foo bar baz'
        b.getControl('Apply').click()
        # reload() forgets the query-paramter, sigh.
        b.open('http://localhost/++skin++vivi/repository'
               '/article/@@edit.form.memo-diver?show_form=1')
        self.assertEqual('foo bar baz', b.getControl('Memo').value)


class WorkflowStatusDisplayTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.ArticleLayer

    def test_displays_status_fields_as_checkboxes(self):
        from zeit.workflow.interfaces import IContentWorkflow
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                somalia = zeit.cms.interfaces.ICMSContent(
                    'http://xml.zeit.de/online/2007/01/Somalia')
                IContentWorkflow(somalia).corrected = True

        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/online/2007/01/Somalia/@@checkout')
        b.open('@@edit.form.workflow-display?show_form=1')
        self.assertFalse(b.getControl('Edited').selected)
        self.assertTrue(b.getControl('Corrected').selected)

    def test_displays_last_published_information(self):
        from zeit.workflow.interfaces import IContentWorkflow
        from zeit.cms.workflow.interfaces import IPublish

        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                article = zeit.cms.interfaces.ICMSContent(
                    'http://xml.zeit.de/online/2007/01/Somalia')
                IContentWorkflow(article).urgent = True
                IPublish(article).publish()
                zeit.workflow.testing.run_publish()
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/online/2007/01/Somalia/@@checkout')
        b.open('@@contents')
        self.assertEllipsis(
            '...zuletzt veröffentlicht am...von...zope.user...', b.contents)
