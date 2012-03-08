# Copyright (c) 2011-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import transaction
import zeit.content.article.testing


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.TestBrowserLayer

    expected_type = NotImplemented

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
            article.xml.body.division[self.expected_type] = ''
            article.xml.body.division[self.expected_type].set(
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
