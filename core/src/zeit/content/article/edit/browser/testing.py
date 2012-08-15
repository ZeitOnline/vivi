# Copyright (c) 2011-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import transaction
import zeit.content.article.testing


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.TestBrowserLayer

    block_type = NotImplemented

    def setUp(self):
        super(BrowserTestCase, self).setUp()
        browser = self.browser
        browser.open('http://localhost:8080/++skin++vivi/repository/online'
                     '/2007/01/Somalia/@@checkout')
        self.article_url = browser.url
        browser.open('@@contents')
        self.contents_url = browser.url

    def get_article(self, with_empty_block=False):
        article = self.layer.setup.getRootFolder()[
            'workingcopy']['zope.user']['Somalia']
        for p in article.xml.findall('//division/*'):
            p.getparent().remove(p)
        if with_empty_block:
            article.xml.body.division[self.block_type] = ''
            article.xml.body.division[self.block_type].set(
                '{http://namespaces.zeit.de/CMS/cp}__name__', 'blockname')
        article._p_changed = True
        transaction.commit()
        return article


class EditorTestCase(zeit.content.article.testing.SeleniumTestCase):

    def add_article(self):
        s = self.selenium
        self.open('/repository')
        s.select('id=add_menu', 'label=Article')
        s.waitForPageToLoad()

    def create(self, contents=None, existing=0):
        s = self.selenium
        s.assertCssCount('css=.block.type-p', existing)
        s.waitForElementPresent('css=.create-paragraph')
        s.click('css=.create-paragraph')
        s.waitForCssCount('css=.block.type-p', existing + 1)
        if contents:
            code = (
                "this.browserbot.findElement("
                "    '//*[contains(@class, \"block\") and"
                "         contains(@class, \"type-p\")][{0}]"
                "     //*[contains(@class, \"editable\")]').innerHTML = '{1}'"
                ).format(existing + 1, contents.replace("'", "\\'"))
            s.getEval(code)

    def save(self, locator='css=.block.type-p .editable'):
        self.selenium.getEval(
            "this.browserbot.findElement('{0}').editable.save()".format(locator))
        self.selenium.waitForElementNotPresent('xpath=//*[@contenteditable]')

    def create_block(self, block, wait_for_inline=False):
        s = self.selenium
        s.click('link=Module')
        s.waitForElementPresent('css=#article-modules .module')
        block_sel = '.block.type-{0}'.format(block)
        s.dragAndDropToObject(
            'css=#article-modules .module[cms\\:block_type={0}]'.format(block),
            'css=#article-editor-text .landing-zone')
        s.waitForElementPresent('css={0}'.format(block_sel))
        if wait_for_inline:
            s.waitForElementPresent(
                'css={0} form.inline-form.wired'.format(block_sel))
        return s.getAttribute('css={0}@id'.format(block_sel))
