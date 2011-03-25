# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.article.testing


class TestUndo(zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(TestUndo, self).setUp()
        self.add_article()

    def test_undo_list_fresh_after_checkout_is_empty(self):
        # where empty at the moment means, contains two entries, one for
        # @@checkout and one for the intial article/@@contents that sets up
        # some GUIDs
        s = self.selenium
        s.waitForXpathCount('//*[@id="cp-undo"]//a', 2)
        s.assertText('//*[@id="cp-undo"]//li[1]/a', '*/@@contents')
        s.assertText('//*[@id="cp-undo"]//li[2]/a', '*/@@checkout')

    def test_change_metadata_and_text_then_revert_undoes_both_changes(self):
        s = self.selenium
        self.test_undo_list_fresh_after_checkout_is_empty()

        s.assertValue('id=head.year', '2008') # before
        s.select('id=head.ressort', 'International') # required field
        s.type('id=head.year', '2010')
        s.fireEvent('id=head.year', 'blur')
        s.waitForElementNotPresent('css=.widget-outer.dirty')
        s.waitForXpathCount('//*[@id="cp-undo"]//a', 3)

        s.assertElementNotPresent('css=.editable p') # before
        self.create()
        s.getEval("this.browserbot.findElement("
                  "  'css=.block.type-p .editable').innerHTML = "
                  "   '<p>Mary had a little</p>'")
        self.save()
        s.waitForElementPresent('css=.editable p:contains(Mary had)')
        # two transactions, create block and save text
        s.waitForXpathCount('//*[@id="cp-undo"]//a', 5)

        # XXX we don't want to undo the @@contents step; it should not show up
        # in the history
        s.click('//*[@id="cp-undo"]//li[position() = last() - 2]/a')
        # undo transaction gets its own entry
        s.waitForXpathCount('//*[@id="cp-undo"]//a', 6)

        # we're back to the 'before' state
        s.assertValue('id=head.year', '2008')
        s.assertElementNotPresent('css=.editable p')
