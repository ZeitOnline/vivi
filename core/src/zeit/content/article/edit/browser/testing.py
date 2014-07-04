# Copyright (c) 2011-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import transaction
import zeit.cms.clipboard.interfaces
import zeit.cms.testing
import zeit.content.article.testing


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.LAYER

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
        article = self.getRootFolder()[
            'workingcopy']['zope.user']['Somalia']
        for p in article.xml.xpath('//division/*'):
            p.getparent().remove(p)
        if with_empty_block:
            article.xml.body.division[self.block_type] = ''
            article.xml.body.division[self.block_type].set(
                '{http://namespaces.zeit.de/CMS/cp}__name__', 'blockname')
        article._p_changed = True
        transaction.commit()
        return article


class EditorHelper(object):

    editable_locator = '.block.type-p .editable'

    def add_article(self, add_location='/repository'):
        s = self.selenium
        self.open(add_location)
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
                u"window.jQuery(window.jQuery('.block.type-p')[{0}])"
                u".find('.editable')[0].innerHTML = '{1}';"
            ).format(existing, contents.replace(u"'", u'\\"'))
            self.run_js(code)
            self.mark_dirty()

    def get_js_editable(self, locator=None):
        if locator is None:
            locator = self.editable_locator
        return "window.jQuery('{0}')[0].editable".format(locator)

    def mark_dirty(self, locator=None, status=True):
        editable = self.get_js_editable(locator)
        self.run_js(
            editable + ".dirty = " + str(status).lower() + ";")

    def save(self, locator=None):
        editable = self.get_js_editable(locator)
        self.run_js(editable + ".save()")
        self.selenium.waitForElementNotPresent('xpath=//*[@contenteditable]')

    def create_block(self, block, wait_for_inline=False):
        s = self.selenium
        s.click('link=Module')
        s.waitForElementPresent('css=#article-modules .module')
        block_sel = '.block.type-{0}'.format(block)
        s.dragAndDropToObject(
            'css=#article-modules .module[cms\\:block_type={0}]'.format(block),
            'css=#editable-body > .landing-zone')
        s.waitForElementPresent('css={0}'.format(block_sel))
        if wait_for_inline:
            s.waitForElementPresent(
                'css={0} form.inline-form.wired'.format(block_sel))
        return s.getAttribute('css={0}@id'.format(block_sel))

    def add_testcontent_to_clipboard(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction() as principal:
                clipboard = zeit.cms.clipboard.interfaces.IClipboard(principal)
                clipboard.addClip('Clip')
                clip = clipboard['Clip']
                clipboard.addContent(
                    clip, self.repository['testcontent'],
                    'testcontent', insert=True)
        transaction.commit()

        s = self.selenium
        s.refresh()
        s.click('//li[@uniqueid="Clip"]')
        s.waitForElementPresent('//li[@uniqueid="Clip"][@action="collapse"]')


class EditorTestCase(zeit.content.article.testing.SeleniumTestCase,
                     EditorHelper):
    pass
