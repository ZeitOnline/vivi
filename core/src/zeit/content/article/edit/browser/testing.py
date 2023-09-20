import transaction
import zeit.cms.clipboard.interfaces
import zeit.content.article.testing
import zope.security.management


class BrowserTestCase(zeit.content.article.testing.BrowserTestCase):

    def setUp(self):
        super().setUp()
        browser = self.browser
        browser.open('http://localhost:8080/++skin++vivi/repository/online'
                     '/2007/01/Somalia/@@checkout')
        self.article_url = browser.url
        browser.open('@@contents')
        self.contents_url = browser.url

    def get_article(self, with_block=None):
        article = self.getRootFolder()[
            'workingcopy']['zope.user']['Somalia']
        for p in article.xml.xpath('//division/*'):
            p.getparent().remove(p)
        if with_block:
            article.xml.body.division[with_block] = ''
            article.xml.body.division[with_block].set(
                '{http://namespaces.zeit.de/CMS/cp}__name__', 'blockname')
        article._p_changed = True
        transaction.commit()
        return article


class EditorHelper:

    editable_locator = '.block.type-p .editable'

    def add_article(self, add_location='/repository'):
        s = self.selenium
        self.open(add_location)
        s.select('id=add_menu', 'label=Article')
        s.waitForElementPresent('css=.create-paragraph')

    def create(self, contents=None, existing=0):
        s = self.selenium
        s.assertCssCount('css=.block.type-p', existing)
        s.waitForElementPresent('css=.create-paragraph')
        s.click('css=.create-paragraph')
        s.waitForCssCount('css=.block.type-p', existing + 1)
        if contents:
            code = (
                "window.jQuery(window.jQuery('.block.type-p')[{0}])"
                ".find('.editable')[0].innerHTML = '{1}';"
            ).format(existing, contents.replace("'", '\\"'))
            self.selenium.runScript(code)
            self.mark_dirty()

    def get_js_editable(self, locator=None):
        if locator is None:
            locator = self.editable_locator
        return "window.jQuery('{0}')[0].editable".format(locator)

    def mark_dirty(self, locator=None, status=True):
        editable = self.get_js_editable(locator)
        self.selenium.runScript(
            editable + ".dirty = " + str(status).lower() + ";")

    def save(self, locator=None):
        editable = self.get_js_editable(locator)
        self.selenium.runScript(editable + ".save()")
        self.selenium.waitForElementNotPresent('xpath=//*[@contenteditable]')

    def create_block(self, block, wait_for_inline=False):
        s = self.selenium
        s.waitForElementPresent('link=Struktur')
        s.waitForNotVisible('css=.message')
        s.click('link=Struktur')
        s.waitForElementPresent('css=#article-modules .module')
        block_sel = '.block.type-{0}'.format(block)
        count = s.getCssCount('css={0}'.format(block_sel))
        s.dragAndDropToObject(
            'css=#article-modules .module[cms\\:block_type={0}]'.format(block),
            'css=#editable-body > .landing-zone', '10,10')
        s.waitForCssCount('css={0}'.format(block_sel), count + 1)
        if wait_for_inline:
            s.waitForElementPresent(
                'css={0} form.inline-form.wired'.format(block_sel))
        return s.getAttribute('css={0}@id'.format(block_sel))

    def add_testcontent_to_clipboard(self):
        transaction.abort()
        principal = (zope.security.management.getInteraction()
                     .participations[0].principal)
        clipboard = zeit.cms.clipboard.interfaces.IClipboard(principal)
        clipboard.addClip('Clip')
        clip = clipboard['Clip']
        clipboard.addContent(
            clip, self.repository['testcontent'],
            'testcontent', insert=True)
        transaction.commit()

        s = self.selenium
        s.refresh()
        s.clickAt('//li[@uniqueid="Clip"]', '10,10')
        s.waitForElementPresent('//li[@uniqueid="Clip"][@action="collapse"]')


class EditorTestCase(zeit.content.article.testing.SeleniumTestCase,
                     EditorHelper):
    window_width = 1600
    window_height = 1000


class RecipeListHelper:

    editable_locator = '.block.type-p .editable'

    def setup_ingredient(self, add_location='/repository'):
        s = self.selenium
        self.add_article()
        self.create_block('recipelist')
        s.waitForElementPresent('//input[@name="add_ingredient"]')

        # Add ingredient
        s.type('//input[@name="add_ingredient"]', 'Brath')
        s.waitForVisible('css=ul.ui-autocomplete li')
        s.click('css=ul.ui-autocomplete li')
