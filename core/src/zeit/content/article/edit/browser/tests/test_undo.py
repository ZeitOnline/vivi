from selenium.webdriver.common.keys import Keys
import zeit.content.article.edit.browser.testing


class TestUndo(zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super().setUp()
        self.add_article()

    def test_undo_list_fresh_after_checkout_is_empty(self):
        s = self.selenium
        s.waitForElementPresent('css=.history ul')
        s.assertElementNotPresent('css=.history a')

    def test_change_metadata_and_text_then_revert_undoes_both_changes(self):
        s = self.selenium
        self.test_undo_list_fresh_after_checkout_is_empty()

        fold = 'css=#edit-form-metadata .fold-link'
        s.waitForElementPresent(fold)
        s.click(fold)

        s.waitForVisible('link=Undo')
        s.click('link=Undo')  # Make undo pane visible

        s.assertValue('id=metadata-b.copyrights', '')  # before
        s.select('id=metadata-b.product', 'Die Zeit')  # required field
        s.type('id=metadata-b.copyrights', 'ZEI')
        s.keyPress('id=metadata-b.copyrights', Keys.TAB)
        s.waitForElementNotPresent('css=.field.dirty')
        s.waitForXpathCount('//*[@id="cp-undo"]//a', 1)
        s.assertText('//*[@id="cp-undo"]//li[1]/a', 'edit metadata')

        s.assertElementNotPresent('css=.editable p')  # before
        self.create()
        s.runScript("window.jQuery("
                    "  '.block.type-p .editable')[0].innerHTML = "
                    "   '<p>Mary had a little</p>'")
        self.mark_dirty()
        self.save()
        s.waitForElementPresent('jquery=.editable p:contains(Mary had)')
        s.waitForXpathCount('//*[@id="cp-undo"]//a', 4)
        s.assertText('//*[@id="cp-undo"]//li[1]/a', 'edit body text')
        s.assertText('//*[@id="cp-undo"]//li[2]/a', "add 'p' block")

        s.click('//*[@id="cp-undo"]//li[position() = last()]/a')
        s.waitForXpathCount('//*[@id="cp-undo"]//a', 5)
        s.assertText('//*[@id="cp-undo"]//li[1]/a',
                     'revert up to "edit metadata"')

        # we're back to the 'before' state
        s.waitForElementPresent('id=metadata-b.copyrights')
        s.waitForValue('id=metadata-b.copyrights', '')
        s.assertElementNotPresent('css=.editable p')

    def test_undo_tab_is_not_shown_in_repository(self):
        # since undo only applies in the workingcopy
        s = self.selenium
        self.open('/repository/online/2007/01/Somalia')
        s.waitForElementPresent('id=cp-library')
        s.assertElementNotPresent('id=cp-undo')
