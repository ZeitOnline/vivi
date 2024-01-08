from unittest import mock
import datetime
import unittest

from selenium.webdriver.common.keys import Keys
import transaction
import zope.component

import zeit.cms.tagging.testing
import zeit.cms.workflow.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.article.testing
import zeit.edit.interfaces
import zeit.edit.rule


class Checkin(zeit.content.article.testing.BrowserTestCase):
    def test_validation_errors_should_be_displayed_at_checkin_button(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/' '@@zeit.content.article.Add')
        b.open('@@edit.form.checkin-errors')
        self.assert_ellipsis(
            """
            ...Ressort:...Required input is missing...
            ...Title:...Required input is missing...
            ...New file name:...Required input is missing...
            ..."""
        )


class CheckinSelenium(
    zeit.content.article.edit.browser.testing.EditorTestCase, zeit.cms.tagging.testing.TaggingHelper
):
    def test_form_with_semantic_change_shows_current_timestamp(self):
        s = self.selenium
        self.open('/repository/online/2007/01/Somalia-Grill/@@checkout')
        s.waitForElementPresent('id=publish.has_semantic_change')
        s.click('id=publish.has_semantic_change')
        s.waitForElementPresent('css=.timer')
        s.waitForNotText('css=.timer', '')
        date_format = '%d.%m.%Y %H:%Mh'
        timestamp = datetime.datetime.now().strftime(date_format)
        if s.getText('css=.timer') != timestamp:
            # the minute has just changed, so we repeat with an updated
            # timestamp but don't expect this to happen again anytime soon
            timestamp = datetime.datetime.now().strftime(date_format)
            s.assertText('css=.timer', timestamp)

    def test_form_without_new_semantic_change_shows_last_timestamp(self):
        s = self.selenium
        self.open('/repository/online/2007/01/Somalia-Grill/@@checkout')
        s.waitForElementPresent('css=.timestamp')
        s.waitForNotText('css=.timestamp', '')
        date_format = '%d.%m.%Y %H:%Mh'
        timestamp = datetime.datetime(2007, 1, 1, 9, 53).strftime(date_format)
        s.assertText('css=.timestamp', timestamp)

    def test_form_without_last_semantic_change_shows_current_timestamp(self):
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
        error = 'jquery=#edit-form-workflow .errors dt:contains(file name)'
        s.waitForElementPresent(error)
        fold = 'css=#edit-form-filename .fold-link'
        s.waitForElementPresent(fold)
        s.click(fold)
        s.type('new-filename.rename_to', 'asdf')
        s.keyPress('new-filename.rename_to', Keys.TAB)
        s.waitForElementNotPresent(error)

    def test_checkin_button_is_disabled_while_validation_errors_present(self):
        self.add_article()
        s = self.selenium

        disabled_checkin_button = 'css=a#checkin.button.disabled'
        s.waitForElementPresent(disabled_checkin_button)

        fold = 'css=#edit-form-metadata .fold-link'
        s.waitForElementPresent(fold)
        s.click(fold)
        s.type('article-content-head.title', 'mytitle')
        s.keyPress('article-content-head.title', Keys.TAB)
        input_ressort = 'metadata-a.ressort'
        s.select(input_ressort, 'label=International')
        s.keyPress('id=metadata-a.sub_ressort', Keys.TAB)  # Trigger blur

        s.click('css=#edit-form-filename .fold-link')
        s.type('new-filename.rename_to', 'asdf')
        s.keyPress('new-filename.rename_to', Keys.TAB)
        s.click('css=#edit-form-keywords .edit-bar .fold-link')
        s.waitForElementNotPresent('css=#edit-form-keywords.folded')
        self.add_keyword_by_autocomplete('testtag', form_prefix='keywords')
        self.add_keyword_by_autocomplete('testtag2', form_prefix='keywords')
        self.add_keyword_by_autocomplete('testtag3', form_prefix='keywords')

        s.waitForElementNotPresent(disabled_checkin_button)

    def test_checkin_does_not_set_last_semantic_change_by_default(self):
        sc = zeit.cms.content.interfaces.ISemanticChange(
            self.repository['online']['2007']['01']['Somalia']
        )
        before = sc.last_semantic_change
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        s = self.selenium
        s.waitForElementPresent('id=checkin')
        s.clickAndWait('id=checkin')
        self.assertIn('repository', s.getLocation())
        self.assertEqual(before, sc.last_semantic_change)

    def test_checkin_sets_last_semantic_change_if_checked(self):
        sc = zeit.cms.content.interfaces.ISemanticChange(
            self.repository['online']['2007']['01']['Somalia']
        )
        before = sc.last_semantic_change
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        s = self.selenium
        s.waitForElementPresent('id=checkin')
        s.click('id=publish.has_semantic_change')
        s.pause(500)
        s.waitForElementNotPresent('css=.field.dirty')
        s.waitForElementPresent('id=publish.has_semantic_change')
        s.waitForChecked('id=publish.has_semantic_change')
        s.clickAndWait('id=checkin')
        self.assertIn('repository', s.getLocation())
        self.assertNotEqual(before, sc.last_semantic_change)

    def test_semantic_change_checkbox_is_saved(self):
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        s = self.selenium
        s.waitForElementPresent('id=checkin')
        s.click('id=publish.has_semantic_change')
        s.pause(500)
        s.waitForElementNotPresent('css=.field.dirty')
        # click something else to trigger a reload of the checkin form
        s.waitForElementPresent('id=publish.urgent')
        s.click('id=publish.urgent')
        s.pause(500)
        s.waitForElementNotPresent('css=.field.dirty')
        s.waitForElementPresent('id=publish.has_semantic_change')
        s.waitForChecked('id=publish.has_semantic_change')

    def test_checkin_button_change_on_semantic_change(self):
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        s = self.selenium
        s.waitForElementPresent('id=checkin')
        s.waitForElementNotPresent('css=.checkin-button.semantic-change')
        s.click('id=publish.has_semantic_change')
        s.waitForChecked('id=publish.has_semantic_change')
        s.waitForElementPresent('css=.checkin-button.semantic-change')
        s.click('id=publish.has_semantic_change')
        s.waitForNotChecked('id=publish.has_semantic_change')
        s.waitForElementNotPresent('css=.checkin-button.semantic-change')

    @unittest.skip(
        'Cannot make the focus/blur-trigger work'
        ' to get the inlineform to submit. Maybe with Webdriver?'
    )
    def test_clicking_checkin_button_triggers_inlineform_save_beforehand(self):
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        s = self.selenium
        s.waitForElementPresent('id=checkin')
        s.runScript(
            """\
zeit.cms.with_lock_calls = [];
zeit.cms.with_lock = function(callable) {
    zeit.cms.with_lock_calls.push(callable);
};"""
        )

        s.click('id=article-content-head.title')
        s.click('id=checkin')
        self.assertEqual(2, self.eval('zeit.cms.with_lock_calls.length'))
        self.assertEqual('MochiKit.Async.doXHR', self.eval('zeit.cms.with_lock_calls[0].NAME'))
        self.assertEqual(None, self.eval('zeit.cms.with_lock_calls[1].NAME'))

    def test_save_state_button_should_load_page(self):
        self.open('/repository/online/2007/01/Somalia')
        s = self.selenium
        s.waitForElementPresent('css=#edit-form-workflow a.save')
        s.clickAndWait('css=#edit-form-workflow a.save')
        # Yeah, not much to assert here. Mainly checkin that the button is
        # there :/
        s.waitForElementPresent('css=#edit-form-workflow a.save')


class WorkflowEndToEnd(zeit.content.article.edit.browser.testing.EditorTestCase):
    def test_checkin_redirects_to_repository(self):
        s = self.selenium
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        s.waitForElementPresent('id=checkin')
        self.assertNotIn('repository', s.getLocation())
        s.clickAndWait('id=checkin')
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
        self.open('/repository/online/2007/01/Somalia/')
        s.waitForElementPresent('id=publish.urgent')
        s.click('id=publish.urgent')
        s.pause(500)
        s.waitForElementNotPresent('css=.field.dirty')
        s.click('id=publish')
        s.waitForElementPresent('css=ol#worklist')
        # lightbox content is covered by zeit.workflow, see there for detailed
        # tests

    def test_save_and_publish_shows_lightbox(self):
        s = self.selenium
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        s.waitForElementPresent('id=publish.urgent')
        s.click('id=publish.urgent')
        s.pause(500)
        s.waitForElementNotPresent('css=.field.dirty')
        s.click('id=checkin-publish')
        s.waitForElementPresent('css=ol#worklist')

    def test_delete_shows_lightbox(self):
        s = self.selenium
        self.open('/repository/online/2007/01/Somalia/')
        s.waitForElementPresent('id=delete_from_repository')
        s.click('id=delete_from_repository')
        s.waitForElementPresent('css=.lightbox')


class Publish(zeit.content.article.testing.BrowserTestCase):
    def test_validation_errors_are_displayed_during_publish(self):
        # Create article with divisions, otherwise the recursive validator has
        # no children to validate
        article = zeit.content.article.testing.create_article()
        article.body.create_item('image')
        self.repository['article_with_division'] = article
        zeit.cms.workflow.interfaces.IPublishInfo(
            self.repository['article_with_division']
        ).urgent = True

        rm = zope.component.getUtility(zeit.edit.interfaces.IRulesManager)
        rules = [rm.create_rule(['error_if(True, "Custom Error")'], 0)]
        with mock.patch.object(zeit.edit.rule.RulesManager, 'rules', rules):
            b = self.browser
            b.open(
                'http://localhost/++skin++vivi/repository/' 'article_with_division/@@publish.html'
            )
        self.assertEllipsis('...Custom Error...', b.contents)


class Delete(zeit.content.article.testing.BrowserTestCase):
    def test_checked_out_article_has_cancel_but_no_delete(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/' 'online/2007/01/Somalia/@@checkout')
        b.open('@@edit.form.checkin-buttons?show_form=1')
        self.assertNothingRaised(b.getLink, 'Cancel')
        self.assertNotIn('Delete', b.contents)

    def test_checked_in_article_has_delete_but_no_cancel(self):
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository'
            '/online/2007/01/Somalia/@@edit.form.checkin-buttons?show_form=1'
        )
        self.assertNothingRaised(b.getLink, 'Delete')
        self.assertNotIn('Cancel', b.contents)


class Objectlog(zeit.content.article.edit.browser.testing.EditorTestCase):
    def test_objectlog_is_wrapped(self):
        # this is a sanity check that the views are wired up correctly
        article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        zeit.objectlog.interfaces.ILog(article).log('example message')
        transaction.commit()
        self.open('/++skin++vivi/repository/online/2007/01/Somalia/')
        s = self.selenium
        fold = 'css=#edit-form-status .fold-link'
        s.waitForElementPresent(fold)
        s.click(fold)
        s.waitForText('css=div.objectlog table.objectlog', '*example message*')
