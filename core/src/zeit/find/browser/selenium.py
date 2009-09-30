# coding: utf8
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.selenium


class TestTabs(zeit.cms.selenium.Test):

    def setUp(self):
        super(TestTabs, self).setUp()
        self.open('/find')
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

    def test_activate_for_this_page(self):
        s = self.selenium
        s.click('link=Für diese Seite')
        s.waitForVisible('id=for-this-page')
        self.assertSelected('for-this-page')


class TestSearch(zeit.cms.selenium.Test):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.open('/find')
        self.selenium.waitForVisible('css=div.teaser_title')

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
        s.click('id=search-type-unknown')
        s.click('id=extended_search_button')
        s.waitForVisible('id=extended_search_info')
        s.verifyNotVisible('id=extended_search')
        s.verifyText('css=#extended_search_info span', 'Unknown Resource')

    def test_last_query_should_be_saved(self):
        s = self.selenium
        s.click('id=extended_search_button')
        s.waitForVisible('id=extended_search')
        s.select('name=product', 'Zeit Online')
        s.type('name=author', 'foo')
        s.select('name=sort_order', 'Datum')
        s.check('id=search-type-channel')
        s.click('id=search_button')
        s.pause(1000)

        self.open('/find')
        self.selenium.waitForVisible('css=div.teaser_title')
        s.click('id=extended_search_button')
        s.waitForVisible('id=extended_search')
        s.verifySelectedLabel('name=product', 'Zeit Online')
        s.verifyValue('name=author', 'foo')
        s.verifySelectedLabel('name=sort_order', 'Datum')
        s.verifyChecked('id=search-type-channel')
