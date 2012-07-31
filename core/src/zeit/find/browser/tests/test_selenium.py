# coding: utf8
# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import pkg_resources
import zeit.cms.testing
import zeit.find.tests
import zope.component


class TestTabs(zeit.cms.testing.SeleniumTestCase):

    layer = zeit.find.tests.SeleniumLayer

    def setUp(self):
        super(TestTabs, self).setUp()
        self.open('/')
        self.open('/find')
        self.selenium.waitForElementPresent('id=fulltext')
        self.selenium.waitForVisible('id=fulltext')

    def assertSelected(self, href):
        self.selenium.verifyElementPresent(
            '//li[@class="selected"]/a[@href="%s"]' % href)

    def test_on_startup_search_should_be_active(self):
        self.assertSelected('search_form')

    def test_activate_favorites(self):
        s = self.selenium
        s.click('link=Favoriten')
        s.waitForVisible('id=favorites')
        self.assertSelected('favorites')


class TestSearch(zeit.cms.testing.SeleniumTestCase):

    layer = zeit.find.tests.SeleniumLayer
    skin = 'vivi'

    def setUp(self):
        import zeit.solr.interfaces
        super(TestSearch, self).setUp()
        self.set_result('defaultqueryresult.json')
        self.open('/')
        self.open('/find')
        self.selenium.waitForElementPresent('css=div.teaser_title')
        self.selenium.waitForVisible('css=div.teaser_title')

    def set_result(self, filename):
        zeit.find.tests.SearchLayer.set_result(__name__, filename)

    def test_relateds(self):
        s = self.selenium
        s.click('css=.related_links')
        s.waitForTextPresent('No related entries could be found.')
        s.click('css=.related_links')
        s.waitForTextNotPresent('No related entries could be found.')

    def test_favorites(self):
        s = self.selenium
        s.click('link=Favoriten')
        s.waitForVisible('id=favorites')
        s.verifyElementNotPresent('css=#favorites .related_links')
        s.click('link=Suche')
        s.click('css=.toggle_favorited')
        s.waitForElementPresent('css=.toggle_favorited.favorited')
        s.click('link=Favoriten')
        s.waitForElementPresent('css=#favorites .related_links')

    def test_extended_search_display(self):
        s = self.selenium
        s.verifyVisible('id=extended_search_info')
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
        s.verifyVisible('id=type_search_info')
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
        self.set_result('empty.json')
        s = self.selenium
        s.click('id=extended_search_button')
        s.waitForVisible('id=extended_search')
        s.select('name=product', 'Zeit Online')
        s.type('name=author', 'foo')
        s.select('name=sort_order', 'Datum')
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

    def test_result_filters_expand_automatically(self):
        s = self.selenium
        s.click('id=result_filters_button')
        s.waitForElementPresent('css=#result_filters_button.unfolded')
        s.pause(500)
        self.open('/find')
        s.waitForElementPresent('css=#result_filters_button.unfolded')

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
        self.eval("zeit.find._search.set_types(['file', 'image'])")
        s.assertChecked('id=search-type-file')
        s.assertNotChecked('id=search-type-collection')
        s.assertChecked('id=search-type-image')
        self.eval("zeit.find._search.set_types(['file', 'collection'])")
        s.assertChecked('id=search-type-file')
        s.assertChecked('id=search-type-collection')
        s.assertNotChecked('id=search-type-image')

    def test_activate_objectbrowser_accepts_types(self):
        s = self.selenium
        s.assertNotChecked('id=search-type-file')
        self.eval("zeit.cms.activate_objectbrowser(['file'])")
        s.assertChecked('id=search-type-file')
