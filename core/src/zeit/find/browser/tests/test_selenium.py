# coding: utf8
from unittest import mock

import zeit.cms.testing
import zeit.find.testing


class TestSearch(zeit.cms.testing.SeleniumTestCase):
    layer = zeit.find.testing.SELENIUM_LAYER
    skin = 'vivi'

    def setUp(self):
        super().setUp()
        zeit.find.testing.LAYER.set_result('zeit.find.tests', 'data/obama.json')
        self.types_patch = mock.patch(
            'zeit.find.browser.find.SearchForm.CONTENT_TYPES',
            new=['collection', 'file', 'image', 'testcontenttype', 'unknown'],
        )
        self.types_patch.start()
        self.open('/find')
        self.selenium.waitForElementPresent('css=div.teaser_title')
        self.selenium.waitForVisible('css=div.teaser_title')

    def tearDown(self):
        self.types_patch.stop()
        super().tearDown()

    def test_authors_displayed_in_search_result(self):
        s = self.selenium
        s.click('id=type_search_button')
        s.waitForElementPresent('css=#type_search_button.unfolded')
        s.pause(500)
        self.open('/find')
        s.waitForElementPresent('css=#type_search_button.unfolded')
        s.verifyText('css=.metadata span:nth-of-type(4)', 'William Shakespeare')

    def test_extended_search_display(self):
        s = self.selenium
        s.verifyNotVisible('id=extended_search')
        s.click('id=extended_search_button')
        s.waitForVisible('id=extended_search')
        s.verifyNotVisible('id=extended_search_info')
        s.type('name=author', 'Foo bar')
        s.click('id=extended_search_button')
        s.waitForVisible('id=extended_search_info')
        s.verifyNotVisible('id=extended_search')
        s.verifyText('css=#extended_search_info span', 'Foo bar')

    def test_type_search_display(self):
        s = self.selenium
        s.verifyNotVisible('id=type_search')
        s.click('id=type_search_button')
        s.waitForVisible('id=type_search')
        s.verifyNotVisible('id=type_search_info')
        s.click('id=search-type-unknown')
        s.click('id=type_search_button')
        s.waitForVisible('id=type_search_info')
        s.verifyNotVisible('id=type_search')
        s.verifyText('css=#type_search_info span', 'Unknown Resource')

    def test_last_query_should_be_saved(self):
        zeit.find.testing.LAYER.search.client.search.return_value = {
            'hits': {'hits': [], 'total': 0}
        }
        s = self.selenium
        s.click('id=extended_search_button')
        s.waitForVisible('id=extended_search')
        s.select('name=product', 'Zeit Online')
        s.type('name=author', 'foo')
        s.select('name=sort_order', 'Datum')
        s.click('id=type_search_button')
        s.waitForVisible('id=type_search')
        s.check('id=search-type-testcontenttype')
        s.click('id=search_button')
        s.pause(1000)

        self.open('/find')
        self.selenium.waitForElementPresent('css=div.no_search_result')
        # The extended_search is already visible as its state is restored, too.
        s.waitForVisible('id=extended_search')
        s.verifySelectedLabel('name=product', 'Zeit Online')
        s.verifyValue('name=author', 'foo')
        s.verifySelectedLabel('name=sort_order', 'Datum')
        s.verifyChecked('id=search-type-testcontenttype')

    def test_type_search_expand_automatically(self):
        s = self.selenium
        s.click('id=type_search_button')
        s.waitForElementPresent('css=#type_search_button.unfolded')
        s.pause(500)
        self.open('/find')
        s.waitForElementPresent('css=#type_search_button.unfolded')

    def test_setting_types_in_search_form(self):
        #  XXX This should be a unit test!
        s = self.selenium
        s.assertNotChecked('id=search-type-file')
        s.assertNotChecked('id=search-type-collection')
        s.assertNotChecked('id=search-type-image')
        self.execute("zeit.find._search.set_types(['file', 'image'])")
        s.assertChecked('id=search-type-file')
        s.assertNotChecked('id=search-type-collection')
        s.assertChecked('id=search-type-image')
        self.execute("zeit.find._search.set_types(['file', 'collection'])")
        s.assertChecked('id=search-type-file')
        s.assertChecked('id=search-type-collection')
        s.assertNotChecked('id=search-type-image')

    def test_activate_objectbrowser_accepts_types(self):
        s = self.selenium
        s.assertNotChecked('id=search-type-file')
        self.execute("zeit.cms.activate_objectbrowser(['file'])")
        s.assertChecked('id=search-type-file')

    def test_audio_type_selection(self):
        s = self.selenium
        s.verifyNotVisible('id=extended_search')
        s.click('id=extended_search_button')
        s.waitForVisible('id=extended_search')
        s.verifyNotVisible('id=extended_search_info')
        s.select('name=audio_type', 'Text to Speech')
        s.verifyValue('name=audio_type', 'tts')
        s.select('name=audio_type', 'Podcast')
        s.verifyValue('name=audio_type', 'podcast')
