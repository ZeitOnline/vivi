# coding: utf8
# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest2
import zeit.cms.testing
import zeit.content.article.testing


class HeadTest(zeit.content.article.testing.SeleniumTestCase):

    def setUp(self):
        super(HeadTest, self).setUp()
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        self.selenium.waitForElementPresent('id=misc-printdata.year')

    def test_form_should_highlight_changed_data(self):
        s = self.selenium
        s.assertValue('id=misc-printdata.year', '2007')
        s.assertElementNotPresent('css=.widget-outer.dirty')
        s.type('id=misc-printdata.year', '2010')
        s.click('id=misc-printdata.volume')
        s.waitForElementPresent('css=.widget-outer.dirty')

    def test_form_should_save_entered_data_on_blur(self):
        s = self.selenium
        s.assertValue('id=misc-printdata.year', '2007')
        s.type('id=misc-printdata.year', '2010')
        s.fireEvent('id=misc-printdata.year', 'blur')
        s.waitForElementNotPresent('css=.widget-outer.dirty')
        # Re-open the page and verify that the data is still there
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent('id=misc-printdata.year')
        s.assertValue('id=misc-printdata.year', '2010')

    def test_change_in_ressort_should_update_subressort_list(self):
        s = self.selenium
        s.assertSelectedLabel('id=metadata-a.ressort', 'International')
        s.pause(100)
        self.assertEqual(
            [u'(no value)', u'Meinung', u'Nahost', u'US-Wahl'],
            s.getSelectOptions('id=metadata-a.sub_ressort'))
        s.select('id=metadata-a.ressort', 'Deutschland')
        s.pause(100)
        self.assertEqual(
            [u'(no value)', u'Datenschutz', u'Integration',
             u'Joschka Fisher', u'Meinung'],
            s.getSelectOptions('id=metadata-a.sub_ressort'))
        s.click('metadata-a.actions.apply')
        s.pause(250)
        self.assertEqual(
            [u'(no value)', u'Datenschutz', u'Integration',
             u'Joschka Fisher', u'Meinung'],
            s.getSelectOptions('id=metadata-a.sub_ressort'))

    def test_invalid_input_should_display_error_message(self):
        s = self.selenium
        s.assertValue('id=misc-printdata.year', '2007')
        s.type('id=misc-printdata.year', 'ASDF')
        s.click('misc-printdata.actions.apply')
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
        s.assertElementNotPresent('css=#edit-form-metadata.folded')
        s.click('css=#edit-form-metadata .edit-bar .fold-link')
        s.waitForElementPresent('css=#edit-form-metadata.folded')
        s.click('css=#edit-form-metadata .edit-bar .fold-link')
        s.waitForElementNotPresent('css=#edit-form-metadata.folded')

    def test_fold_should_survive_page_load(self):
        s = self.selenium
        s.assertElementNotPresent('css=#edit-form-metadata.folded')
        s.click('css=#edit-form-metadata .edit-bar .fold-link')
        s.waitForElementPresent('css=#edit-form-metadata.folded')
        s.open(s.getLocation())
        s.waitForElementPresent('css=#edit-form-metadata.folded')

    def test_unfold_should_be_stored(self):
        s = self.selenium
        s.assertElementNotPresent('css=#edit-form-metadata.folded')
        s.click('css=#edit-form-metadata .edit-bar .fold-link')
        s.waitForElementPresent('css=#edit-form-metadata.folded')
        s.click('css=#edit-form-metadata .edit-bar .fold-link')
        s.waitForElementNotPresent('css=#edit-form-metadata.folded')
        s.open(s.getLocation())
        s.waitForElementPresent('css=#edit-form-metadata')
        s.assertElementNotPresent('css=#edit-form-metadata.folded')


class ReadonlyTest(zeit.content.article.testing.SeleniumTestCase):

    def setUp(self):
        super(ReadonlyTest, self).setUp()
        self.open('/repository/online/2007/01/Somalia/')
        self.open('/repository/online/2007/01/Somalia/@@edit.html')

    def test_head_should_be_readonly_visible(self):
        self.assert_widget_text("misc-printdata.year", '2007')
        self.assert_widget_text("metadata-a.ressort", 'International')

    def test_navigation_should_readonly_visible(self):
        self.assert_widget_text("metadata-c.__name__", 'Somalia')
        self.assert_widget_text("metadata-b.copyrights", 'ZEIT online')
        s = self.selenium
        s.waitForElementPresent('xpath=//input[@id="metadata-b.dailyNewsletter"]')
        s.assertAttribute(
            'xpath=//input[@id="metadata-b.dailyNewsletter"]@disabled',
            'regexp:disabled|true')
        s.assertNotChecked('xpath=//input[@id="metadata-b.dailyNewsletter"]')

    def test_texts_should_be_readonly_visible(self):
        self.assert_widget_text('article-content-head.title', u'Rückkehr der Warlords')
        self.assert_widget_text('article-content-head.subtitle', 'Im Zuge des*')

    def test_assets_should_be_readonly_visible(self):
        from zeit.cms.checkout.helper import checked_out
        from zeit.cms.related.interfaces import IRelatedContent
        import zeit.cms.interfaces
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                content = zeit.cms.interfaces.ICMSContent(
                    'http://xml.zeit.de/online/2007/01/Somalia')
                with checked_out(content) as co:
                    IRelatedContent(co).related = (
                        zeit.cms.interfaces.ICMSContent(
                            'http://xml.zeit.de/testcontent'),)
        s = self.selenium
        s.open(s.getLocation())
        self.assert_widget_text('assets.related', '*testcontent*')


class KeywordTest(zeit.content.article.testing.SeleniumTestCase):

    def get_tag(self, code):
        tag = mock.Mock()
        tag.code = tag.label = code
        tag.disabled = False
        return tag

    def setup_tags(self, *codes):
        import stabledict
        tags = stabledict.StableDict()
        for code in codes:
            tags[code] = self.get_tag(code)
        patcher = mock.patch('zeit.cms.tagging.interfaces.ITagger')
        self.addCleanup(patcher.stop)
        tagger = patcher.start()
        tagger.return_value = tags
        return tags

    def test_sorting_should_trigger_write(self):
        s = self.selenium
        tags = self.setup_tags('t1', 't2', 't3')
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        s.waitForElementPresent('id=metadata-a.keywords')
        s.dragAndDropToObject("xpath=//li[contains(., 't1')]",
                              "xpath=//li[contains(., 't3')]")
        s.assertTextPresent('t2*t3*t1')
        s.pause(500)
        self.assertEqual(3, tags['t2'].weight)
        self.assertEqual(2, tags['t3'].weight)
        self.assertEqual(1, tags['t1'].weight)


class AuthorTest(zeit.content.article.testing.SeleniumTestCase):

    def setUp(self):
        super(AuthorTest, self).setUp()
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        self.selenium.waitForElementPresent('id=metadata-c.author_references')

    def test_authors_should_be_inline_addable(self):
        s = self.selenium
        s.click('//*[@id="metadata-c.author_references"]//a[@rel = "show_add_view"]')
        s.waitForElementPresent('id=form.firstname')
        s.type('id=form.firstname', 'Ben')
        s.type('id=form.lastname', 'Utzer')
        s.select('id=form.status', 'index=1')
        s.click('id=form.actions.add')
        s.waitForTextPresent('Ben Utzer')
