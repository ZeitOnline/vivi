# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.testing.mock
import mock
import unittest2
import zeit.cms.tagging.testing
import zeit.cms.testing


class DisplayWidget(zeit.cms.testing.BrowserTestCase,
                    zeit.cms.tagging.testing.TaggingHelper):

    def test_customised_widget_renders_a_list_with_shown_items(self):
        self.setup_tags('t1', 't2', 't3')
        with mock.patch(
            'zeit.cms.tagging.interfaces.KeywordConfiguration.keywords_shown',
            gocept.testing.mock.Property()) as keywords_shown:
            keywords_shown.return_value = 2
            self.browser.handleErrors = False
            self.browser.open(
                'http://localhost/++skin++vivi/repository/testcontent')
            self.assertEllipsis(
                '...<li class=" shown">...'
                '<li class=" shown">...',
                self.browser.contents)
            self.assertNotEllipsis('t3', self.browser.contents)


class InputWidget(zeit.cms.testing.SeleniumTestCase,
                  zeit.cms.tagging.testing.TaggingHelper):

    def open_content(self):
        self.open('/repository/testcontent/@@checkout')
        s = self.selenium
        s.windowMaximize()
        s.type('name=form.year', '2011')
        s.select('name=form.ressort', 'label=Deutschland')
        s.type('name=form.title', 'Test')
        s.type('name=form.authors.0.', 'Hans Wurst')

    def test_tags_should_be_sortable(self):
        self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.assertTextPresent('t1*t2*t3*t4')
        s.dragAndDropToObject(
            "xpath=//li[contains(., 't1')]",
            "xpath=//li[contains(., 't3')]")
        s.assertTextPresent('t2*t3*t1*t4')

    def test_sorted_tags_should_be_saved(self):
        self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.dragAndDropToObject(
            "xpath=//li[contains(., 't1')]",
            "xpath=//li[contains(., 't3')]")
        s.assertTextPresent('t2*t3*t1*t4')
        s.clickAndWait('name=form.actions.apply')
        self.assertEqual(
            ['t2', 't3', 't1', 't4'],
            list(self.tagger().updateOrder.call_args[0][0]))

    @unittest2.skip("Selenium doesn't do d'n'd on jqueryui sortable.")
    def test_change_event_is_triggered_on_sorting_tags(self):
        self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.dragAndDropToObject(
            "xpath=//li[contains(., 't1')]",
            "xpath=//li[contains(., 't3')]")
        s.assertTextPresent('t2*t3*t1*t4')
        # XXX

    def test_unchecked_tags_should_be_disabled(self):
        self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.click("xpath=//li[contains(., 't1')]/label")
        s.clickAndWait('name=form.actions.apply')
        self.assertNotIn('t1', self.tagger())
        self.assertIn('t2', self.tagger())

    def test_view_should_not_break_without_tagger(self):
        self.open_content()
        self.selenium.assertTextPresent('Keywords')

    def test_update_should_load_tags(self):
        tags = self.setup_tags()
        self.open_content()
        s = self.selenium
        tags['t1'] = self.get_tag('t1')
        s.click('name=update_tags')
        s.waitForTextPresent('t1')
        self.assertTrue(self.tagger().update.called)

    def test_save_should_work_after_update(self):
        self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.click('update_tags')
        s.pause(100)
        s.clickAndWait('name=form.actions.apply')
        s.waitForTextPresent('t1')

    def test_configured_number_of_items_is_marked(self):
        with mock.patch(
            'zeit.cms.tagging.interfaces.KeywordConfiguration.keywords_shown',
            gocept.testing.mock.Property()) as keywords_shown:
            keywords_shown.return_value = 2

            self.setup_tags('t1', 't2', 't3')
            self.open_content()
            s = self.selenium
            s.click('update_tags')
            s.waitForCssCount('css=.fieldname-keywords li.not-shown', 1)
            s.waitForCssCount('css=.fieldname-keywords li.shown', 2)
