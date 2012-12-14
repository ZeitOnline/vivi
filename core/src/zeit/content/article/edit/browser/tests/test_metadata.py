# coding: utf8
# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from unittest2 import skip
import transaction
import zeit.cms.tagging.testing
import zeit.content.article.edit.browser.testing


class HeadTest(zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(HeadTest, self).setUp()
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        self.selenium.waitForElementPresent('id=options-b.year')

    def test_form_should_highlight_changed_data(self):
        s = self.selenium
        s.assertValue('id=options-b.year', '2007')
        s.assertElementNotPresent('css=.widget-outer.dirty')
        s.type('id=options-b.year', '2010')
        s.click('id=options-b.volume')
        s.waitForElementPresent('css=.field.dirty')

    def test_form_should_save_entered_text_on_blur(self):
        s = self.selenium
        s.assertValue('id=options-b.year', '2007')
        s.type('id=options-b.year', '2010')
        s.fireEvent('id=options-b.year', 'blur')
        s.waitForElementNotPresent('css=.field.dirty')
        # Re-open the page and verify that the data is still there
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent('id=options-b.year')
        s.assertValue('id=options-b.year', '2010')

    def test_form_should_save_selection_on_blur(self):
        s = self.selenium
        s.select('id=metadata-b.product', 'Zeit Magazin')
        s.fireEvent('id=metadata-b.product', 'blur')
        s.waitForElementNotPresent('css=.field.dirty')
        s.assertSelectedLabel('id=metadata-b.product', 'Zeit Magazin')

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
        s.assertValue('id=options-b.year', '2007')
        s.type('id=options-b.year', 'ASDF')
        s.click('options-b.actions.apply')
        s.waitForElementPresent('css=.inline-form div.error')

    def test_relateds_should_be_addable(self):
        self.add_testcontent_to_clipboard()
        s = self.selenium
        s.waitForElementPresent('id=internallinks.related')
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/testcontent"]',
            'xpath=//*[@id="internallinks.related"]//ul')
        s.waitForElementPresent(
            'xpath=//*[@id="internallinks.related"]//li[1]')

    def test_galleries_should_use_drop_widget(self):
        s = self.selenium
        s.waitForElementPresent(
           'css=.drop-object-widget input[name="leadteaser.gallery"]')

    def test_metadata_should_be_foldable_and_unfoldable(self):
        s = self.selenium
        s.waitForElementPresent('css=#edit-form-metadata.folded')
        s.click('css=#edit-form-metadata .edit-bar .fold-link')
        s.waitForElementNotPresent('css=#edit-form-metadata.folded')
        s.click('css=#edit-form-metadata .edit-bar .fold-link')
        s.waitForElementPresent('css=#edit-form-metadata.folded')

    def test_unfold_should_be_stored(self):
        s = self.selenium
        s.waitForElementPresent('css=#edit-form-metadata.folded')
        s.click('css=#edit-form-metadata .edit-bar .fold-link')
        s.waitForElementNotPresent('css=#edit-form-metadata.folded')
        s.open(s.getLocation())
        s.waitForElementPresent('css=#edit-form-metadata')
        s.assertElementNotPresent('css=#edit-form-metadata.folded')


class KeywordTest(zeit.content.article.edit.browser.testing.EditorTestCase,
                  zeit.cms.tagging.testing.TaggingHelper):

    @skip("no d'n'd 'til webdriver")
    def test_sorting_should_trigger_write(self):
        s = self.selenium
        self.setup_tags('t1', 't2', 't3')
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        s.waitForElementPresent('id=metadata-a.keywords')
        s.waitForTextPresent('t1*t2*t3')
        s.dragAndDropToObject(
            "xpath=//li[contains(., 't1')]",
            "xpath=//li[contains(., 't3')]")
        s.pause(200)
        self.assertEqual(
            ['t2', 't1', 't3'],
            list(self.tagger().updateOrder.call_args[0][0]))

    def test_helptext_should_be_shown_for_new_article(self):
        self.add_article()
        s = self.selenium
        s.waitForElementPresent('id=keywords.keywords')
        s.assertTextPresent('Only the first 6 keywords are shown')

    def test_helptext_should_not_be_shown_for_existing_article(self):
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        s = self.selenium
        s.waitForElementPresent('id=keywords.keywords')
        s.assertNotTextPresent('Only the first 6 keywords are shown')


class MetadataTest(zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(MetadataTest, self).setUp()
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        self.selenium.waitForElementPresent('id=options-b.year')

    def test_comments_allowed_toggled_when_comments_section_is_toggled(self):
        s = self.selenium
        s.waitForElementNotPresent('metadata-comments.commentsAllowed')
        s.click('metadata-comments.commentSectionEnable')
        s.waitForElementPresent('metadata-comments.commentsAllowed')
        s.click('metadata-comments.commentSectionEnable')
        s.waitForElementNotPresent('metadata-comments.commentsAllowed')

    def test_disallow_comments_if_comments_section_is_disabled(self):
        s = self.selenium
        s.waitForElementNotPresent('metadata-comments.commentsAllowed')
        s.click('metadata-comments.commentSectionEnable')
        s.waitForElementPresent('metadata-comments.commentsAllowed')
        s.click('metadata-comments.commentsAllowed')
        s.waitForChecked('metadata-comments.commentsAllowed')
        s.click('metadata-comments.commentSectionEnable')
        s.waitForElementNotPresent('metadata-comments.commentsAllowed')
        s.click('metadata-comments.commentSectionEnable')
        s.waitForElementPresent('metadata-comments.commentsAllowed')
        s.waitForNotChecked('metadata-comments.commentsAllowed')


@skip('Drag&Drop does not work, the icon is never dropped on the clipboard')
class HeaderTest(zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_icon_in_header_is_draggable_to_clipboard(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction() as principal:
                clipboard = zeit.cms.clipboard.interfaces.IClipboard(principal)
                clipboard.addClip('Clip')
                transaction.commit()

        self.open('/repository/online/2007/01/Somalia')
        s = self.selenium
        clipboard = '//li[@uniqueid="Clip"]'
        s.click(clipboard)
        s.waitForElementPresent('//li[@uniqueid="Clip"][@action="collapse"]')

        icon = 'css=#editor-forms-heading .content-icon'
        s.waitForElementPresent(icon)
        s.dragAndDropToObject(icon, clipboard)
        s.waitForElementPresent(
            clipboard + '//span[contains(@class, "uniqueId") and '
            'contains(text(), "Somalia")]')
