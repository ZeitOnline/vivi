# coding: utf-8
from unittest import mock
import json
import unittest

from selenium.webdriver.common.by import By
import gocept.testing.mock
import zope.component

import zeit.cms.tagging.interfaces
import zeit.cms.tagging.tag
import zeit.cms.tagging.testing
import zeit.cms.testing


class DisplayWidget(
    zeit.cms.testing.ZeitCmsBrowserTestCase, zeit.cms.tagging.testing.TaggingHelper
):
    def test_renders_keyword_labels(self):
        self.setup_tags('t1', 't2', 't3')
        self.browser.open('http://localhost/++skin++vivi/repository/testcontent')
        self.assertEllipsis('...<li>...t1...<li>...t2...', self.browser.contents)

    def test_highlights_keywords_with_topicpage(self):
        tags = self.setup_tags('t1', 't2', 't3')
        self.add_topicpage_link(tags['t1'])
        self.browser.open('http://localhost/++skin++vivi/repository/testcontent')
        self.assertEllipsis('...<li>...<a...class="with-topic-page"...t1...', self.browser.contents)
        self.assertTrue(1, self.browser.contents.count('with-topic-page'))

    def test_keyword_links_to_topicpage(self):
        tags = self.setup_tags('t1', 't2', 't3')
        self.add_topicpage_link(tags['t1'])
        self.browser.open('http://localhost/++skin++vivi/repository/testcontent')
        self.assertEllipsis(
            '...<li>...<a...href="http://localhost/live-prefix/thema/t1"' '...t1...',
            self.browser.contents,
        )


class InputWidget(zeit.cms.testing.ZeitCmsBrowserTestCase, zeit.cms.tagging.testing.TaggingHelper):
    def test_serializes_tag_ids_with_unicode_escapes(self):
        self.setup_tags('Bärlin')
        self.browser.open('http://localhost/++skin++vivi/repository/testcontent/@@checkout')
        self.assertEllipsis(r'...tag://...B\\xe4rlin...', self.browser.contents)


class UpdateTags(zeit.cms.testing.ZeitCmsBrowserTestCase, zeit.cms.tagging.testing.TaggingHelper):
    def test_serializes_tag_ids_with_unicode_escapes(self):
        self.setup_tags('Bärlin')
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/testcontent/@@checkout')
        b.open('@@update_tags')
        self.assertEqual(
            [
                {
                    'code': 'tag://test\\u2603B\\xe4rlin',
                    'label': 'Bärlin (Test)',
                    'pinned': False,
                }
            ],
            json.loads(b.contents)['tags'],
        )


class InputWidgetUI(zeit.cms.testing.SeleniumTestCase, zeit.cms.tagging.testing.TaggingHelper):
    layer = zeit.cms.testing.WEBDRIVER_LAYER

    window_width = 1600
    window_height = 1000

    def setUp(self):
        super().setUp()
        self.patches = gocept.testing.mock.Patches()
        display = self.patches.add(
            'zeit.cms.tagging.browser.widget.Widget.display_update_button',
            gocept.testing.mock.Property(),
        )
        display.return_value = True

    def tearDown(self):
        self.patches.reset()
        super().tearDown()

    def open_content(self):
        self.open('/repository/testcontent/@@checkout')
        s = self.selenium
        s.type('name=form.year', '2011')
        s.select('name=form.ressort', 'label=Deutschland')
        s.type('name=form.title', 'Test')
        s.type('name=form.authors.0.', 'Hans Wurst')

    @unittest.skip("Selenium doesn't do d'n'd on jqueryui sortable.")
    def test_tags_should_be_sortable(self):
        self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.assertText('id=form.keywords.list', '*t1*t2*t3*t4*')
        s.dragAndDropToObject('jquery=li:contains(t1)', 'jquery=li:contains(t3)')
        s.assertText('id=form.keywords.list', '*t2*t3*t1*t4*')
        # XXX check that sorting triggers a change event (inlineforms need it)

    @unittest.skip("Selenium doesn't do d'n'd on jqueryui sortable.")
    def test_sorted_tags_should_be_saved(self):
        self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.dragAndDropToObject('jquery=li:contains(t1)', 'jquery=li:contains(t3)')
        s.assertText('id=form.keywords.list', '*t2*t3*t1*t4*')
        s.clickAndWait('name=form.actions.apply')
        self.assertEqual(['t2', 't3', 't1', 't4'], list(self.tagger().updateOrder.call_args[0][0]))

    def test_unchecked_tags_should_be_disabled(self):
        self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.waitForNotVisible('css=.message')
        s.click('jquery=li:contains(t1) .delete')
        s.click('name=form.actions.apply')
        s.waitForTextPresent('t2')
        self.assertNotIn('t1', self.tagger())
        self.assertIn('t2', self.tagger())

    def test_view_should_not_break_without_tagger(self):
        self.open_content()
        self.selenium.assertTextPresent('Keywords')

    def test_update_should_load_tags(self):
        tags = self.setup_tags()
        self.open_content()
        s = self.selenium
        tags['t1'] = zeit.cms.tagging.tag.Tag('t1', entity_type='test')
        s.click('name=update_tags')
        s.waitForTextPresent('t1')
        self.assertTrue(self.tagger().update.called)

    def test_update_should_trigger_highlight_tags_call(self):
        with mock.patch('zeit.cms.tagging.browser.widget.UpdateTags.json') as mocked:
            self.open_content()
            s = self.selenium
            s.click('name=update_tags')
            s.pause(100)
            self.assertTrue(mocked.called)

    def test_save_should_work_after_update_regardless_of_prior_state(self):
        self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.waitForNotVisible('css=.message')
        s.click('jquery=li:contains(t1) .delete')
        s.click('name=update_tags')
        s.pause(100)
        s.clickAndWait('name=form.actions.apply')
        s.waitForTextPresent('t1')

    def test_can_add_tags_via_autocomplete_field(self):
        self.setup_tags()
        whitelist = zope.component.queryUtility(zeit.cms.tagging.interfaces.IWhitelist)
        whitelist.tags.append('Kohle')
        self.open_content()
        s = self.selenium
        self.add_keyword_by_autocomplete('Kohle')
        s.clickAndWait('name=form.actions.apply')
        s.waitForTextPresent('Kohle')

    def test_toggle_pinned_should_display_pinned_icon(self):
        self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.waitForNotVisible('css=.message')
        s.click('jquery=li:contains(t1) .toggle-pin')
        s.clickAndWait('name=form.actions.apply')
        s.waitForElementPresent('jquery=li:contains(t1) .pinned')
        s.assertNotTextPresent('Wrong contained type')

    def test_tags_with_topicpages_are_highlighted(self):
        tags = self.setup_tags('t1', 't2', 't3', 't4')
        self.add_topicpage_link(tags['t1'])
        self.open_content()
        sel = self.selenium
        sel.assertXpathCount('//li/a[@href="http://localhost/live-prefix/thema/t1"]', 1)
        self.assertEqual(
            'with-topic-page',
            sel.selenium.find_element(By.LINK_TEXT, 't1 (Test)').get_attribute('class'),
        )
        sel.assertXpathCount('//li/a[@href="http://localhost/live-prefix/thema/t2"]', 0)
