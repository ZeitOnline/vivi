# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.article.edit.browser.testing


class AudioEditTest(zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_layout_should_be_editable(self):
        s = self.selenium
        self.add_article()
        self.create_block('audio')
        # XXX a label-selector would be nice (gocept.selenium #6492)
        input = 'css=.block.type-audio form.wired input'
        s.waitForElementPresent(input)
        s.type(input, 'asdf')
        s.fireEvent(input, 'blur')
        s.waitForElementNotPresent('css=.widget-outer.dirty')
        # Re-open the page and verify that the data is still there
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent(input)
        s.assertValue(input, 'asdf')
