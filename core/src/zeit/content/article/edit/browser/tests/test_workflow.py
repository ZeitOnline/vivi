# coding: utf-8
# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.article.article import Article
from zeit.workflow.interfaces import IReview
import datetime
import mock
import unittest2 as unittest
import zeit.cms.testing
import zeit.content.article.testing


class Checkin(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.ArticleLayer

    def test_validation_errors_should_be_displayed_at_checkin_button(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                self.repository['article'] = Article()
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/article/@@checkout')
        b.handleErrors = False
        b.open('@@edit.form.checkin')
        self.assert_ellipsis('...Title:...Required input is missing...')
        self.assertTrue(b.getControl('Save').disabled)


class CheckinSelenium(
    zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_checkin_form_shows_current_timestamp(self):
        s = self.selenium
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        s.waitForElementPresent('css=.timer')
        s.waitForNotText('css=.timer', '')
        date_format = '%d.%m.%Y %H:%Mh'
        timestamp = datetime.datetime.now().strftime(date_format)
        if s.getText('css=.timer') != timestamp:
            # the minute has just changed, so we repeat with an updated
            # timestamp but don't expect this to happen again anytime soon
            timestamp = datetime.datetime.now().strftime(date_format)
            s.assertText('css=.timer', timestamp)

    def test_validation_errors_are_removed_from_checkin_form_on_change(self):
        self.add_article()
        s = self.selenium
        title_error = 'css=#edit-form-workflow .errors dt:contains(Title)'
        s.waitForElementPresent(title_error)
        input_title = 'article-content-head.title'
        # XXX type() doesn't work with selenium-1 and FF>7
        self.eval(
            'document.getElementById("%s").value = "mytitle"' % input_title)
        s.fireEvent(input_title, 'blur')
        s.waitForElementNotPresent(title_error)

    def test_checkin_does_not_set_last_semantic_change_by_default(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            sc = zeit.cms.content.interfaces.ISemanticChange(
                self.repository['online']['2007']['01']['Somalia'])
        before = sc.last_semantic_change
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        s = self.selenium
        s.waitForElementPresent('id=checkin')
        s.clickAndWait('id=checkin')
        self.assertIn('repository', s.getLocation())
        self.assertEqual(before, sc.last_semantic_change)

    def test_checkin_sets_last_semantic_change_if_checked(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            sc = zeit.cms.content.interfaces.ISemanticChange(
                self.repository['online']['2007']['01']['Somalia'])
        before = sc.last_semantic_change
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        s = self.selenium
        s.waitForElementPresent('id=checkin')
        s.click('id=publish.has_semantic_change')
        s.waitForElementNotPresent('css=.field.dirty')
        s.assertValue('id=publish.has_semantic_change', 'on')
        s.clickAndWait('id=checkin')
        self.assertIn('repository', s.getLocation())
        self.assertNotEqual(before, sc.last_semantic_change)

    def test_semantic_change_checkbox_is_saved(self):
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        s = self.selenium
        s.waitForElementPresent('id=checkin')
        s.click('id=publish.has_semantic_change')
        s.waitForElementNotPresent('css=.field.dirty')
        # click something else to trigger a reload of the checkin form
        s.click('id=publish.urgent')
        s.waitForElementNotPresent('css=.field.dirty')
        s.assertValue('id=publish.has_semantic_change', 'on')


class WorkflowEndToEnd(
    zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_checkin_redirects_to_repository(self):
        s = self.selenium
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        s.waitForElementPresent('name=checkin')
        self.assertNotIn('repository', s.getLocation())
        s.clickAndWait('name=checkin')
        self.assertIn('repository', s.getLocation())

    def test_checkout_redirects_to_working_copy(self):
        s = self.selenium
        self.open('/repository/online/2007/01/Somalia/')
        checkout_button = 'xpath=//a[contains(@title, "Checkout")]'
        s.waitForElementPresent(checkout_button)
        self.assertIn('repository', s.getLocation())
        s.clickAndWait(checkout_button)
        self.assertNotIn('repository', s.getLocation())

    def test_publish_shows_lightbox(self):
        s = self.selenium
        self.open('/')  # XXX else the next open() fails as Unauthenticated
        self.open('/repository/online/2007/01/Somalia/')
        s.waitForElementPresent('id=publish')
        s.click('id=publish')
        s.waitForElementPresent('css=.lightbox')
        # lightbox content is covered by zeit.workflow, see there for detailed
        # tests

    def test_delete_shows_lightbox(self):
        s = self.selenium
        self.open('/') # XXX
        self.open('/repository/online/2007/01/Somalia/')
        s.waitForElementPresent('id=delete_from_repository')
        s.click('id=delete_from_repository')
        s.waitForElementPresent('css=.lightbox')


class Publish(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.ArticleLayer

    def prepare_content(self, urgent):
        root = self.getRootFolder()
        with zeit.cms.testing.site(root):
            with zeit.cms.testing.interaction():
                content = zeit.cms.interfaces.ICMSContent(
                    'http://xml.zeit.de/online/2007/01/Somalia')
                IReview(content).urgent = urgent

    def test_smoke_publish_button_publishes_article(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/'
               'online/2007/01/Somalia/@@checkout')
        b.open('@@edit.form.publish?show_form=1')
        b.getControl('Urgent').selected = True
        with mock.patch('zeit.cms.workflow.interfaces.IPublish') as publish:
            b.handleErrors = False
            b.getControl('Save & Publish').click()
            self.assertTrue(publish().publish.called)

    def test_urgent_denies_marking_edited_and_corrected(self):
        self.prepare_content(urgent=True)
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/'
               'online/2007/01/Somalia/@@checkout')
        b.open('@@edit.form.publish?show_form=1')
        self.assertTrue(b.getControl('Corrected').disabled)
        self.assertTrue(b.getControl('Edited').disabled)

    def test_non_urgent_allows_marking_edited_and_corrected(self):
        self.prepare_content(urgent=False)
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/'
               'online/2007/01/Somalia/@@checkout')
        b.open('@@edit.form.publish?show_form=1')
        self.assertFalse(b.getControl('Corrected').disabled)
        self.assertFalse(b.getControl('Edited').disabled)


class Delete(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.ArticleLayer

    def test_checked_out_article_has_cancel_but_no_delete(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/'
               'online/2007/01/Somalia/@@checkout')
        b.open('@@edit.form.checkin?show_form=1')
        self.assertNothingRaised(b.getLink, 'Cancel')
        self.assertNotIn('Delete', b.contents)

    def test_checked_in_article_has_delete_but_no_cancel(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/'
               'online/2007/01/Somalia/@@edit.form.checkin?show_form=1')
        self.assertNothingRaised(b.getLink, 'Delete')
        self.assertNotIn('Cancel', b.contents)


@unittest.skip('FF shows an HTTP auth dialog for no reason')
class Objectlog(
    zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_objectlog_is_wrapped(self):
        # this is a sanity check that the views are wired up correctly
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                article = zeit.cms.interfaces.ICMSContent(
                    'http://xml.zeit.de/online/2007/01/Somalia')
                zeit.objectlog.interfaces.ILog(article).log('example message')
        self.open(
            'http://localhost/++skin++vivi/repository/online/2007/01/Somalia/')
        s = self.selenium
        s.waitForElementPresent('css=div.objectlog table.objectlog')
        s.assertText('css=div.objectlog table.objectlog', '*example message*')
