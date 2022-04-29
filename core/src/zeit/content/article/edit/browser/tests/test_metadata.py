from selenium.webdriver.common.keys import Keys
from zeit.cms.checkout.helper import checked_out
from zeit.cms.interfaces import ICMSContent
import transaction
import unittest
import zeit.cms.tagging.testing
import zeit.content.article.edit.browser.testing
import zeit.content.author.author
import zope.security.management


class HeadTest(zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(HeadTest, self).setUp()
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        s = self.selenium
        s.waitForElementPresent('id=options-b.year')
        s.click('css=#edit-form-misc .fold-link')

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
        s._find('id=options-b.year').clear()
        s.waitForElementNotPresent('css=.field.dirty')
        s.type('id=options-b.year', '2010')
        s.keyPress('id=options-b.volume', Keys.TAB)  # Trigger blur
        s.waitForElementNotPresent('css=.field.dirty')
        # Re-open the page and verify that the data is still there
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent('id=options-b.year')
        s.assertValue('id=options-b.year', '2010')

    def test_form_should_save_selection_on_blur(self):
        s = self.selenium
        s.click('css=#edit-form-metadata .fold-link')
        s.select('id=metadata-b.product', 'Zeit Magazin')
        s.keyPress('id=metadata-b.copyrights', Keys.TAB)  # Trigger blur
        s.waitForElementNotPresent('css=.field.dirty')
        s.pause(500)
        s.assertSelectedLabel('id=metadata-b.product', 'Zeit Magazin')

    def test_change_in_ressort_should_update_subressort_list(self):
        s = self.selenium
        s.click('css=#edit-form-metadata .fold-link')
        s.assertSelectedLabel('id=metadata-a.ressort', 'International')
        s.pause(100)
        self.assertEqual(
            ['(nothing selected)', 'Meinung', 'Nahost', 'US-Wahl'],
            s.getSelectOptions('id=metadata-a.sub_ressort'))
        s.select('id=metadata-a.ressort', 'Deutschland')
        s.pause(100)
        self.assertEqual(
            ['(nothing selected)', 'Datenschutz', 'Integration',
             'Joschka Fisher', 'Meinung'],
            s.getSelectOptions('id=metadata-a.sub_ressort'))
        s.keyPress('id=metadata-a.sub_ressort', Keys.TAB)  # Trigger blur
        s.pause(500)
        self.assertEqual(
            ['(nothing selected)', 'Datenschutz', 'Integration',
             'Joschka Fisher', 'Meinung'],
            s.getSelectOptions('id=metadata-a.sub_ressort'))

    def test_invalid_input_should_display_error_message(self):
        s = self.selenium
        s.assertValue('id=options-b.year', '2007')
        s.type('id=options-b.year', 'ASDF')
        s.keyPress('id=options-b.volume', Keys.TAB)  # Trigger blur
        s.waitForElementPresent('css=.inline-form div.error')

    def test_relateds_should_be_addable(self):
        self.add_testcontent_to_clipboard()
        s = self.selenium
        fold = 'css=#edit-form-internallinks .fold-link'
        s.waitForElementPresent(fold)
        s.click(fold)
        self.eval('document.querySelector("%s").scrollIntoView()' %
                  fold.replace('css=', ''))
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/testcontent"]',
            'xpath=//*[@id="internallinks.related"]//ul')
        s.waitForElementPresent(
            'xpath=//*[@id="internallinks.related"]//li[1]')

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

    @unittest.skip("no d'n'd 'til webdriver")
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


class MetadataTest(zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(MetadataTest, self).setUp()
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        self.selenium.waitForElementPresent('id=options-b.year')
        self.selenium.click('css=#edit-form-metadata .fold-link')

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

    def test_comments_premoderate_option_is_available(self):
        s = self.selenium
        s.click('metadata-comments.commentSectionEnable')
        s.waitForElementPresent('metadata-comments.commentsPremoderate')


@unittest.skip(
    'Drag&Drop does not work, the icon is never dropped on the clipboard')
class HeaderTest(zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_icon_in_header_is_draggable_to_clipboard(self):
        principal = (zope.security.management.getInteraction()
                     .participations[0].principal)
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


class AuthorLocationTest(
        zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(AuthorLocationTest, self).setUp()
        shakespeare = zeit.content.author.author.Author()
        shakespeare.firstname = 'William'
        shakespeare.lastname = 'Shakespeare'
        self.repository['shakespeare'] = shakespeare
        with checked_out(ICMSContent(
                'http://xml.zeit.de/online/2007/01/Somalia')) as co:
            co.authorships = [co.authorships.create(
                self.repository['shakespeare'])]

    def test_entering_location_via_autocomplete(self):
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        s = self.selenium
        fold = 'css=#edit-form-metadata .fold-link'
        s.waitForElementPresent(fold)
        s.click(fold)
        location_input = 'css=.object-details.type-author .autocomplete-widget'
        s.waitForElementPresent(location_input)
        self.execute(
            'document.querySelector("%s").scrollIntoView()' %
            location_input.replace('css=', ''))
        self.add_by_autocomplete('Paris', location_input)

        s.pause(500)  # Workflow area is reloaded on each InlineForm submit.
        s.clickAndWait('id=checkin')
        location_display = 'css=.object-details.type-author .widget'
        s.waitForElementPresent(location_display)
        s.waitForText(location_display, 'Paris')


class FilenameTest(zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_filename_input_is_wired_up(self):
        self.add_article()
        s = self.selenium
        fold = 'css=#edit-form-filename .fold-link'
        s.waitForElementPresent(fold)
        s.click(fold)
        input_filename = 'new-filename.rename_to'
        s.waitForElementPresent(input_filename)
        s.type(input_filename, 'foo bar')
        s.keyPress(input_filename, Keys.TAB)
        s.waitForValue(input_filename, 'foo-bar')
