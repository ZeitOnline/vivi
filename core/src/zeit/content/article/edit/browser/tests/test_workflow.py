from unittest import mock
import unittest

from selenium.webdriver.common.keys import Keys
import pendulum
import transaction
import zope.component

from zeit.cms.content.sources import FEATURE_TOGGLES
import zeit.cms.tagging.testing
import zeit.cms.workflow.interfaces
import zeit.content.article.edit.browser.testing
import zeit.content.article.edit.interfaces
import zeit.content.article.testing
import zeit.edit.interfaces
import zeit.edit.rule
import zeit.workflow.scheduled.interfaces


class Checkin(zeit.content.article.testing.BrowserTestCase):
    def test_validation_errors_should_be_displayed_at_checkin_button(self):
        b = self.browser
        b.open('/repository/@@zeit.content.article.Add')
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
    def setUp(self):
        super().setUp()
        zeit.cms.content.interfaces.ISemanticChange(
            self.repository['article']
        ).last_semantic_change = pendulum.datetime(2007, 1, 1, 8, 53)
        transaction.commit()

    def test_form_with_semantic_change_shows_current_timestamp(self):
        s = self.selenium
        self.open('/repository/article/@@checkout')
        s.waitForElementPresent('id=publish.has_semantic_change')
        s.click('id=publish.has_semantic_change')
        s.waitForElementPresent('css=.timer')
        s.waitForNotText('css=.timer', '')
        date_format = '%d.%m.%Y %H:%Mh'
        timestamp = pendulum.now('Europe/Berlin').strftime(date_format)
        if s.getText('css=.timer') != timestamp:
            # the minute has just changed, so we repeat with an updated
            # timestamp but don't expect this to happen again anytime soon
            timestamp = pendulum.now('Europe/Berlin').strftime(date_format)
            s.assertText('css=.timer', timestamp)

    def test_form_without_new_semantic_change_shows_last_timestamp(self):
        s = self.selenium
        self.open('/repository/article/@@checkout')
        s.waitForElementPresent('css=.timestamp')
        s.waitForNotText('css=.timestamp', '')
        date_format = '%d.%m.%Y %H:%Mh'
        timestamp = pendulum.datetime(2007, 1, 1, 9, 53).strftime(date_format)
        s.assertText('css=.timestamp', timestamp)

    def test_form_without_last_semantic_change_shows_current_timestamp(self):
        zeit.cms.content.interfaces.ISemanticChange(
            self.repository['article']
        ).last_semantic_change = None
        transaction.commit()
        s = self.selenium
        self.open('/repository/article/@@checkout')
        s.waitForElementPresent('css=.timer')
        s.waitForNotText('css=.timer', '')
        date_format = '%d.%m.%Y %H:%Mh'
        timestamp = pendulum.now('Europe/Berlin').strftime(date_format)
        if s.getText('css=.timer') != timestamp:
            # the minute has just changed, so we repeat with an updated
            # timestamp but don't expect this to happen again anytime soon
            timestamp = pendulum.now('Europe/Berlin').strftime(date_format)
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
        sc = zeit.cms.content.interfaces.ISemanticChange(self.repository['article'])
        before = sc.last_semantic_change
        self.open('/repository/article/@@checkout')
        s = self.selenium
        s.waitForElementPresent('id=checkin')
        s.clickAndWait('id=checkin')
        self.assertIn('repository', s.getLocation())
        transaction.abort()
        self.assertEqual(before, sc.last_semantic_change)

    def test_checkin_sets_last_semantic_change_if_checked(self):
        sc = zeit.cms.content.interfaces.ISemanticChange(self.repository['article'])
        before = sc.last_semantic_change
        self.open('/repository/article/@@checkout')
        s = self.selenium
        s.waitForElementPresent('id=checkin')
        s.click('id=publish.has_semantic_change')
        s.pause(500)
        s.waitForElementNotPresent('css=.field.dirty')
        s.waitForElementPresent('id=publish.has_semantic_change')
        s.waitForChecked('id=publish.has_semantic_change')
        s.clickAndWait('id=checkin')
        self.assertIn('repository', s.getLocation())
        transaction.abort()
        self.assertNotEqual(before, sc.last_semantic_change)

    def test_semantic_change_checkbox_is_saved(self):
        self.open('/repository/article/@@checkout')
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
        self.open('/repository/article/@@checkout')
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
        self.open('/repository/article/@@checkout')
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
        self.open('/repository/article')
        s = self.selenium
        s.waitForElementPresent('css=#edit-form-workflow a.save')
        s.clickAndWait('css=#edit-form-workflow a.save')
        # Yeah, not much to assert here. Mainly checkin that the button is
        # there :/
        s.waitForElementPresent('css=#edit-form-workflow a.save')


class WorkflowEndToEnd(zeit.content.article.edit.browser.testing.EditorTestCase):
    def test_checkin_redirects_to_repository(self):
        s = self.selenium
        self.open('/repository/article/@@checkout')
        s.waitForElementPresent('id=checkin')
        self.assertNotIn('repository', s.getLocation())
        s.clickAndWait('id=checkin')
        self.assertIn('repository', s.getLocation())

    def test_checkout_redirects_to_working_copy(self):
        s = self.selenium
        self.open('/repository/article/')
        checkout_button = 'xpath=//a[contains(@title, "Checkout")]'
        s.waitForElementPresent(checkout_button)
        self.assertIn('repository', s.getLocation())
        s.clickAndWait(checkout_button)
        self.assertNotIn('repository', s.getLocation())

    def test_publish_shows_lightbox(self):
        s = self.selenium
        self.open('/repository/article/')
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
        self.open('/repository/article/@@checkout')
        s.waitForElementPresent('id=publish.urgent')
        s.click('id=publish.urgent')
        s.pause(500)
        s.waitForElementNotPresent('css=.field.dirty')
        s.click('id=checkin-publish')
        s.waitForElementPresent('css=ol#worklist')

    def test_delete_shows_lightbox(self):
        s = self.selenium
        self.open('/repository/article/')
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
            b.open('/repository/article_with_division/@@publish.html')
        self.assertEllipsis('...Custom Error...', b.contents)


class Delete(zeit.content.article.testing.BrowserTestCase):
    def test_checked_out_article_has_cancel_but_no_delete(self):
        b = self.browser
        b.open('/repository/article/@@checkout')
        b.open('@@edit.form.checkin-buttons?show_form=1')
        self.assertNothingRaised(b.getLink, 'Cancel')
        self.assertNotIn('Delete', b.contents)

    def test_checked_in_article_has_delete_but_no_cancel(self):
        b = self.browser
        b.open('/repository/article/@@edit.form.checkin-buttons?show_form=1')
        self.assertNothingRaised(b.getLink, 'Delete')
        self.assertNotIn('Cancel', b.contents)


class Objectlog(zeit.content.article.edit.browser.testing.EditorTestCase):
    def test_objectlog_is_wrapped(self):
        # this is a sanity check that the views are wired up correctly
        article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/article')
        zeit.objectlog.interfaces.ILog(article).log('example message')
        transaction.commit()
        self.open('/++skin++vivi/repository/article')
        s = self.selenium
        fold = 'css=#edit-form-status .fold-link'
        s.waitForElementPresent(fold)
        s.click(fold)
        s.waitForText('css=div.objectlog table.objectlog', '*example message*')


class ScheduledOperationsAccess(zeit.content.article.testing.BrowserTestCase):
    def test_scheduled_access_form_hidden_without_feature_toggle(self):
        FEATURE_TOGGLES.unset('use_scheduled_operations')

        b = self.browser
        b.open('/repository/article/@@edit.form.scheduled-access-operation?show_form=1')
        self.assertEqual('', b.contents.strip())

    def test_scheduled_access_form_can_create_operation(self):
        b = self.browser
        b.open('/repository/article/@@edit.form.scheduled-access-operation?show_form=1')

        scheduled_time = pendulum.now('UTC').add(hours=2)
        b.getControl(
            name='scheduled-access-operation.scheduled_on'
        ).value = scheduled_time.strftime('%Y-%m-%d %H:%M')
        b.getControl(name='scheduled-access-operation.access').displayValue = [
            'access-registration'
        ]
        b.getControl('Apply').click()

        article = self.repository['article']
        ops = zeit.workflow.scheduled.interfaces.IScheduledOperations(article)
        operations = ops.list('publish')
        self.assertEqual(1, len(operations))
        self.assertEqual('registration', operations[0].property_changes.get('access'))

    def test_scheduled_access_form_displays_existing_operation(self):
        article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/article')
        ops = zeit.workflow.scheduled.interfaces.IScheduledOperations(article)
        scheduled_time = pendulum.now('UTC').add(hours=2)
        ops.add('publish', scheduled_time, property_changes={'access': 'abo'})
        transaction.commit()

        b = self.browser
        b.open('/repository/article/@@edit.form.scheduled-access-operation?show_form=1')
        self.assertIn('access-abo', b.contents)

    def test_scheduled_access_form_can_update_operation(self):
        article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/article')
        ops = zeit.workflow.scheduled.interfaces.IScheduledOperations(article)
        scheduled_time = pendulum.now('UTC').add(hours=2)
        op_id = ops.add('publish', scheduled_time, property_changes={'access': 'abo'})
        transaction.commit()

        b = self.browser
        b.open('/repository/article/@@edit.form.scheduled-access-operation?show_form=1')
        new_time = pendulum.now('UTC').add(hours=3)
        b.getControl(name='scheduled-access-operation.scheduled_on').value = new_time.strftime(
            '%Y-%m-%d %H:%M'
        )
        b.getControl(name='scheduled-access-operation.access').displayValue = [
            'access-registration'
        ]
        b.getControl('Apply').click()

        article = self.repository['article']
        ops = zeit.workflow.scheduled.interfaces.IScheduledOperations(article)
        operation = ops.get(op_id)
        self.assertEqual('registration', operation.property_changes.get('access'))

    def test_scheduled_access_form_can_remove_operation(self):
        article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/article')
        ops = zeit.workflow.scheduled.interfaces.IScheduledOperations(article)
        scheduled_time = pendulum.now('UTC').add(hours=2)
        ops.add('publish', scheduled_time, property_changes={'access': 'abo'})
        transaction.commit()

        b = self.browser
        b.open('/repository/article/@@edit.form.scheduled-access-operation?show_form=1')
        b.getControl(name='scheduled-access-operation.scheduled_on').value = ''
        b.getControl('Apply').click()

        article = self.repository['article']
        ops = zeit.workflow.scheduled.interfaces.IScheduledOperations(article)
        self.assertEqual(0, len(ops.list('publish')))


class ScheduledOperationsChannel(zeit.content.article.testing.BrowserTestCase):
    def test_scheduled_channel_form_hidden_without_feature_toggle(self):
        FEATURE_TOGGLES.unset('use_scheduled_operations')

        b = self.browser
        b.open('/repository/article/@@edit.form.scheduled-channel-operation?show_form=1')
        self.assertEqual('', b.contents.strip())

    def test_scheduled_channel_form_renders_without_operation(self):
        b = self.browser
        b.open('/repository/article/@@edit.form.scheduled-channel-operation?show_form=1')
        self.assertIn('scheduled-channel-operation.scheduled_on', b.contents)
        self.assertIn('scheduled-channel-operation.channels', b.contents)

    def test_scheduled_channel_form_can_create_operation(self):
        b = self.browser
        b.open('/repository/article/@@edit.form.scheduled-channel-operation?show_form=1')

        scheduled_time = pendulum.now('UTC').add(hours=1)
        b.getControl(
            name='scheduled-channel-operation.scheduled_on'
        ).value = scheduled_time.strftime('%Y-%m-%d %H:%M')
        # Note: Channel widget is complex, this is a simplified test
        b.getControl('Apply').click()

        # Verify form doesn't crash
        self.assertIn('scheduled-channel-operation', b.url)

    def test_scheduled_channel_form_displays_existing_operation(self):
        article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/article')
        ops = zeit.workflow.scheduled.interfaces.IScheduledOperations(article)
        scheduled_time = pendulum.now('UTC').add(hours=2)
        ops.add(
            'publish', scheduled_time, property_changes={'channels': (('International', None),)}
        )
        transaction.commit()

        b = self.browser
        b.open('/repository/article/@@edit.form.scheduled-channel-operation?show_form=1')
        self.assertIn('International', b.contents)


class ScheduledOperationsSelenium(zeit.content.article.edit.browser.testing.EditorTestCase):
    def test_all_workflow_forms_create_multiple_scheduled_operations(self):
        s = self.selenium
        self.open('/repository/article/@@checkout')

        fold = 'css=#edit-form-workflow-time .fold-link'
        s.waitForElementPresent(fold)
        s.click(fold)

        s.waitForElementPresent('id=timebased.release_period.combination_00')
        released_from = pendulum.now('UTC').add(hours=2)
        released_to = pendulum.now('UTC').add(hours=5)
        s.type(
            'id=timebased.release_period.combination_00',
            released_from.strftime('%Y-%m-%d %H:%M:%S'),
        )
        s.type(
            'id=timebased.release_period.combination_01', released_to.strftime('%Y-%m-%d %H:%M:%S')
        )

        channel_time = pendulum.now('UTC').add(hours=3)
        s.type(
            'id=scheduled-channel-operation.scheduled_on', channel_time.strftime('%Y-%m-%d %H:%M')
        )
        s.keyPress('id=scheduled-channel-operation.scheduled_on', Keys.TAB)

        s.waitForElementPresent('name=scheduled-channel-operation.channels.add')
        s.click('name=scheduled-channel-operation.channels.add')
        s.waitForElementPresent('id=scheduled-channel-operation.channels.0..combination_00')
        s.select('scheduled-channel-operation.channels.0..combination_00', 'Wissen')
        s.waitForElementPresent('id=scheduled-channel-operation.scheduled_on')

        s.waitForElementPresent('id=scheduled-access-operation.scheduled_on')
        access_time = pendulum.now('UTC').add(hours=2)
        s.type('id=scheduled-access-operation.scheduled_on', access_time.strftime('%Y-%m-%d %H:%M'))
        s.select('id=scheduled-access-operation.access', 'label=access-registration')
        s.keyPress('id=scheduled-access-operation.access', Keys.TAB)
        s.keyPress('id=scheduled-access-operation.scheduled_on', Keys.TAB)
        s.waitForElementPresent('id=checkin')
        s.clickAndWait('id=checkin')

        article = self.repository['article']
        ops = zeit.workflow.scheduled.interfaces.IScheduledOperations(article)

        publish_ops = ops.list('publish')
        self.assertEqual(3, len(publish_ops))

        retract_ops = ops.list('retract')
        self.assertEqual(1, len(retract_ops))

        access_ops = [op for op in publish_ops if 'access' in op.property_changes]
        self.assertEqual(1, len(access_ops))
        self.assertEqual('registration', access_ops[0].property_changes['access'])

        channel_ops = [op for op in publish_ops if 'channels' in op.property_changes]
        self.assertEqual(1, len(channel_ops))
        self.assertEqual([['Wissen', None]], channel_ops[0].property_changes['channels'])

        s.waitForElementPresent('id=timebased.release_period.combination_00')
        s.waitForElementPresent('id=scheduled-access-operation.access')
        s.waitForElementPresent('id=scheduled-channel-operation.scheduled_on')
