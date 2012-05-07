# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.article.edit.browser.testing


class TestUndo(zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(TestUndo, self).setUp()
        self.add_article()

    def test_undo_list_fresh_after_checkout_is_empty(self):
        s = self.selenium
        s.waitForElementPresent('css=.history ul')
        s.assertElementNotPresent('css=.history a')

    def test_change_metadata_and_text_then_revert_undoes_both_changes(self):
        s = self.selenium
        self.test_undo_list_fresh_after_checkout_is_empty()

        s.waitForElementPresent('id=metadata-b.copyrights')
        s.assertValue('id=metadata-b.copyrights', '') # before
        s.select('id=metadata-b.product', 'Die Zeit') # required field
        s.type('id=metadata-b.copyrights', 'ZEI')
        s.fireEvent('id=metadata-b.copyrights', 'blur')
        s.waitForElementNotPresent('css=.field.dirty')
        s.waitForXpathCount('//*[@id="cp-undo"]//a', 1)
        s.assertText('//*[@id="cp-undo"]//li[1]/a', 'edit metadata')

        s.assertElementNotPresent('css=.editable p') # before
        self.create()
        s.getEval("this.browserbot.findElement("
                  "  'css=.block.type-p .editable').innerHTML = "
                  "   '<p>Mary had a little</p>'")
        self.save()
        s.waitForElementPresent('css=.editable p:contains(Mary had)')
        s.waitForXpathCount('//*[@id="cp-undo"]//a', 3)
        s.assertText('//*[@id="cp-undo"]//li[1]/a', 'edit body text')
        s.assertText('//*[@id="cp-undo"]//li[2]/a', "add 'p' block")

        s.click('//*[@id="cp-undo"]//li[position() = last()]/a')
        s.waitForXpathCount('//*[@id="cp-undo"]//a', 4)
        s.assertText('//*[@id="cp-undo"]//li[1]/a',
                     'revert up to "edit metadata"')

        # we're back to the 'before' state
        s.assertValue('id=metadata-b.copyrights', '')
        s.assertElementNotPresent('css=.editable p')
