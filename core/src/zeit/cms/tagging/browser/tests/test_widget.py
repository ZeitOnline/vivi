import gocept.testing.mock
import mock
import unittest
import zeit.cms.tagging.testing
import zeit.cms.testing


class DisplayWidget(zeit.cms.testing.ZeitCmsBrowserTestCase,
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
            self.assertNotIn('t3', self.browser.contents)


class InputWidget(zeit.cms.testing.SeleniumTestCase,
                  zeit.cms.tagging.testing.TaggingHelper):

    layer = zeit.cms.testing.WEBDRIVER_LAYER

    def setUp(self):
        super(InputWidget, self).setUp()
        self.patches = gocept.testing.mock.Patches()
        display = self.patches.add(
            'zeit.cms.tagging.browser.widget.Widget.display_update_button',
            gocept.testing.mock.Property())
        display.return_value = True

    def tearDown(self):
        self.patches.reset()
        super(InputWidget, self).tearDown

    def open_content(self):
        self.open('/repository/testcontent/@@checkout')
        s = self.selenium
        s.windowMaximize()
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
        s.dragAndDropToObject(
            'jquery=li:contains(t1)', 'jquery=li:contains(t3)')
        s.assertText('id=form.keywords.list', '*t2*t3*t1*t4*')
        # XXX check that sorting triggers a change event (inlineforms need it)

    @unittest.skip("Selenium doesn't do d'n'd on jqueryui sortable.")
    def test_sorted_tags_should_be_saved(self):
        self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.dragAndDropToObject(
            'jquery=li:contains(t1)', 'jquery=li:contains(t3)')
        s.assertText('id=form.keywords.list', '*t2*t3*t1*t4*')
        s.clickAndWait('name=form.actions.apply')
        self.assertEqual(
            ['t2', 't3', 't1', 't4'],
            list(self.tagger().updateOrder.call_args[0][0]))

    def test_unchecked_tags_should_be_disabled(self):
        self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.click('jquery=li:contains(t1) .delete')
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

    def test_save_should_work_after_update_regardless_of_prior_state(self):
        self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.click('jquery=li:contains(t1) .delete')
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

    def test_can_add_tags_via_autocomplete_field(self):
        self.setup_tags()
        self.open_content()
        s = self.selenium
        self.add_keyword_by_autocomplete('Kohle')
        s.clickAndWait('name=form.actions.apply')
        s.waitForTextPresent('Kohle')

    def test_toggle_pinned_should_display_pinned_icon(self):
        self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.click('jquery=li:contains(t1) .toggle-pin')
        s.clickAndWait('name=form.actions.apply')
        s.waitForElementPresent('jquery=li:contains(t1) .pinned')
        s.assertNotTextPresent('Wrong contained type')

    def test_after_autocomplete_add_shown_markings_are_updated(self):
        with mock.patch(
            'zeit.cms.tagging.interfaces.KeywordConfiguration.keywords_shown',
            gocept.testing.mock.Property()) as keywords_shown:
            keywords_shown.return_value = 1

            self.open_content()
            s = self.selenium
            self.add_keyword_by_autocomplete('Polarkreis')
            self.add_keyword_by_autocomplete('Kohle')
            s.clickAndWait('name=form.actions.apply')
            s.waitForElementPresent('jquery=li.shown:contains(Kohle)')
            s.assertCssCount('css=.fieldname-keywords li.not-shown', 1)
            s.assertCssCount('css=.fieldname-keywords li.shown', 1)
