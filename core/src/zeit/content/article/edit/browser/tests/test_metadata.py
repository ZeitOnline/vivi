# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.article.testing


class HeadTest(zeit.content.article.testing.SeleniumTestCase):

    def setUp(self):
        super(HeadTest, self).setUp()
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        self.selenium.waitForElementPresent('id=head.year')

    def test_form_should_highlight_changed_data(self):
        s = self.selenium
        s.assertValue('id=head.year', '2007')
        s.assertElementNotPresent('css=.widget-outer.dirty')
        s.type('id=head.year', '2010')
        s.click('id=head.volume')
        s.waitForElementPresent('css=.widget-outer.dirty')

    def test_form_should_save_entered_data_on_blur(self):
        s = self.selenium
        s.assertValue('id=head.year', '2007')
        s.type('id=head.year', '2010')
        s.fireEvent('id=head.year', 'blur')
        s.waitForElementNotPresent('css=.widget-outer.dirty')
        # Re-open the page and verify that the data is still there
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent('id=head.year')
        s.assertValue('id=head.year', '2010')

    def test_change_in_ressort_should_update_subressort_list(self):
        s = self.selenium
        s.assertSelectedLabel('id=head.ressort', 'International')
        s.pause(100)
        self.assertEqual(
            [u'(no value)', u'Meinung', u'Nahost', u'US-Wahl'],
            s.getSelectOptions('id=head.sub_ressort'))
        s.select('id=head.ressort', 'Deutschland')
        s.pause(100)
        self.assertEqual(
            [u'(no value)', u'Datenschutz', u'Integration',
             u'Joschka Fisher', u'Meinung'],
            s.getSelectOptions('id=head.sub_ressort'))
        s.click('head.actions.apply')
        s.pause(250)
        self.assertEqual(
            [u'(no value)', u'Datenschutz', u'Integration',
             u'Joschka Fisher', u'Meinung'],
            s.getSelectOptions('id=head.sub_ressort'))

    def test_invalid_input_should_display_error_message(self):
        s = self.selenium
        s.assertValue('id=head.year', '2007')
        s.type('id=head.year', 'ASDF')
        s.click('head.actions.apply')
        s.waitForElementPresent('css=.inline-form div.error')

    def test_relateds_should_be_addable(self):
        s = self.selenium
        # Prepare clipboard
        s.click('id=clip-add-folder-link')
        s.type('id=clip-add-folder-title', 'Favoriten')
        s.click('id=clip-add-folder-submit')
        s.waitForElementPresent('css=#ClipboardPanel li[uniqueId="Favoriten"]')
        s.click('css=#ClipboardPanel li[uniqueId="Favoriten"]')
        s.waitForElementPresent('css=#ClipboardPanel li[action=collapse]')

        # Clip two elements
        self.open('/repository/online/2007/01/eta-zapatero')
        s.dragAndDropToObject(
            'css=#breadcrumbs li:last-child a',
            'css=#ClipboardPanel li[uniqueId="Favoriten"]')
        s.waitForElementPresent('css=#ClipboardPanel ul > li > ul > li')
        self.open('/repository/online/2007/01/Saarland')
        s.dragAndDropToObject(
            'css=#breadcrumbs li:last-child a',
            'css=#ClipboardPanel li[uniqueId="Favoriten"] a')
        s.waitForElementPresent('css=#ClipboardPanel ul > li > ul > li + li')

        # Open editor again
        s.clickAndWait('css=#WorkingcopyPanel td a')
        self.selenium.waitForElementPresent('id=assets.related')

        # Add elements to widget
        s.dragAndDropToObject(
            'css=#ClipboardPanel ul > li > ul > li > ul > li:first-child',
            'xpath=//*[@id="assets.related"]//ul')
        s.waitForElementPresent(
            'xpath=//*[@id="assets.related"]//li[1]')
        s.dragAndDropToObject(
            'css=#ClipboardPanel ul > li > ul > li ul > li:nth-child(2)',
            'xpath=//*[@id="assets.related"]//ul')
        s.waitForElementPresent(
            'xpath=//*[@id="assets.related"]//li[2]')

    def test_galleries_should_use_drop_widget(self):
        s = self.selenium
        s.waitForElementPresent(
           'css=.drop-object-widget input[name="assets.gallery"]')

    def test_metadata_should_be_foldable_and_unfoldable(self):
        s = self.selenium
        s.assertElementNotPresent('css=#article-metadata.folded')
        s.click('css=#article-metadata .edit-bar .fold-link')
        s.waitForElementPresent('css=#article-metadata.folded')
        s.click('css=#article-metadata .edit-bar .fold-link')
        s.waitForElementNotPresent('css=#article-metadata.folded')

    def test_fold_should_survive_page_load(self):
        s = self.selenium
        s.assertElementNotPresent('css=#article-metadata.folded')
        s.click('css=#article-metadata .edit-bar .fold-link')
        s.waitForElementPresent('css=#article-metadata.folded')
        s.open(s.getLocation())
        s.waitForElementPresent('css=#article-metadata.folded')

    def test_unfold_should_be_stored(self):
        s = self.selenium
        s.assertElementNotPresent('css=#article-metadata.folded')
        s.click('css=#article-metadata .edit-bar .fold-link')
        s.waitForElementPresent('css=#article-metadata.folded')
        s.click('css=#article-metadata .edit-bar .fold-link')
        s.waitForElementNotPresent('css=#article-metadata.folded')
        s.open(s.getLocation())
        s.waitForElementPresent('css=#article-metadata')
        s.assertElementNotPresent('css=#article-metadata.folded')
