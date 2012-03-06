# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.article.testing


class EditorTestCase(zeit.content.article.testing.SeleniumTestCase):

    def add_article(self):
        s = self.selenium
        self.open('/repository')
        s.select('id=add_menu', 'label=Article')
        s.waitForPageToLoad()

    def create(self, contents=None):
        s = self.selenium
        s.assertElementNotPresent('css=.block.type-p')
        s.waitForElementPresent('link=Create paragraph')
        s.click('link=Create paragraph')
        s.waitForElementPresent('css=.block.type-p')
        s.click('css=.block.type-p .editable')
        if contents:
            s.getEval(
                "this.browserbot.findElement("
                "  'css=.block.type-p .editable').innerHTML = '{0}'".format(
                    contents.replace("'", "\\'")))

    def save(self, locator='css=.block.type-p .editable'):
        self.selenium.getEval(
            "window.MochiKit.Signal.signal("
            "   this.browserbot.findElement('{0}'), 'save')".format(locator))
        self.selenium.waitForElementNotPresent('xpath=//*[@contenteditable]')

    def create_block(self, block, wait_for_inline=False):
        s = self.selenium
        s.click('link=Module')
        s.waitForElementPresent('css=#article-modules .module')
        block_sel = '.block.type-{0}'.format(block)
        s.dragAndDropToObject(
            'css=#article-modules .module[cms\\:block_type={0}]'.format(block),
            'css=#article-editor-text .landing-zone.visible')
        s.waitForElementPresent('css={0}'.format(block_sel))
        if wait_for_inline:
            s.waitForElementPresent(
                'css={0} form.inline-form.wired'.format(block_sel))
        return s.getAttribute('css={0}@id'.format(block_sel))
