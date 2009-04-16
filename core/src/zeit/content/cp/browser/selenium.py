# coding: utf8
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.repository.interfaces
import zeit.cms.selenium
import zeit.cms.testcontenttype.testcontenttype
import zope.component


class Test(zeit.cms.selenium.Test):

    def open_centerpage(self):
        s = self.selenium
        self.open('/repository')
        s.selectAndWait('id=add_menu', 'label=CenterPage')
        s.type('form.__name__', 'cp')
        s.type('form.title', 'Deutschland')
        s.type('form.authors.0.', 'Hans Wurst')
        s.select('form.ressort', 'Deutschland')
        s.clickAndWait('id=form.actions.add')
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent('xpath=//div[@class="landing-zone"]')


class TestGenericEditing(Test):

    def test_insert(self):
        self.open_centerpage()
        s = self.selenium
        s.verifyElementNotPresent('css=a.choose-block')
        s.click('link=*Add block*')
        s.waitForElementPresent('css=a.choose-block')
        s.click('css=a.choose-block')
        s.waitForElementPresent('css=div.block-types')
        s.click('link=List of teasers')
        s.waitForElementPresent('css=div.block.type-teaser')
        s.click('css=div.block.type-teaser > * > div.edit > a')
        s.waitForElementPresent('id=lightbox.form')
        s.type('form.title', 'Holladrio')
        s.click('form.actions.apply')
        s.waitForElementNotPresent('id=lightbox')

        # Open delete verification
        s.pause(0.5)
        s.click('css=a.delete-link')
        s.waitForElementPresent('css=div.confirm-delete')
        s.verifyElementPresent('css=div.block-inner.highlight')

        # Clicking anywhere else but on the remove confirmer, does close the
        # confirm but does not issue any action. Note that we've got to click
        # on the #confirm-delete-overlay which overlays everything.
        s.click("css=#confirm-delete-overlay")
        s.waitForElementNotPresent('css=div.confirm-delete')
        s.verifyElementNotPresent('css=div.block-inner.highlight')

        # Now really delete
        s.click('css=a.delete-link')
        s.click('css=div.confirm-delete > a')
        s.waitForElementNotPresent('css=a.delete-link')

    def test_close_choose_type_lightbox_does_not_break_editor(self):
        self.open_centerpage()
        s = self.selenium
        s.click('link=*Add block*')
        s.waitForElementPresent('css=a.choose-block')
        s.click('//a[@class="choose-block"]')
        s.waitForElementPresent('css=div.block-types')
        s.click('css=a.CloseButton')
        s.waitForElementNotPresent('css=a.CloseButton')

        # The following click used to do nothing. Make sure it does add a block.
        s.click('link=*Add block*')
        s.waitForXpathCount('//a[@class="choose-block"]', 2)


    def test_hover(self):
        self.open_centerpage()
        s = self.selenium

        # Create a block
        s.click('link=*Add block*')
        s.waitForElementPresent('css=a.choose-block')
        s.click('//a[@class="choose-block"]')
        s.waitForElementPresent('css=div.block-types')
        s.click('link=List of teasers')
        s.waitForElementPresent('css=div.type-teaser')

        # Hover mouse over block
        s.verifyElementNotPresent('css=div.block.hover')
        s.mouseOver('css=div.teaser-list')
        s.verifyElementPresent('css=div.hover')
        s.mouseOut('css=div.teaser-list')
        s.verifyElementNotPresent('css=div.block.hover')


class TestTeaserList(Test):

    def create_clip(self):
        # Creat clip
        s = self.selenium
        s.click('id=clip-add-folder-link')
        s.type('id=clip-add-folder-title', 'Clip')
        s.click('id=clip-add-folder-submit')
        s.waitForElementPresent('link=Clip')
        # Open clip
        s.click('//li[@uniqueid="Clip"]')
        s.waitForElementPresent('//li[@uniqueid="Clip"][@action="collapse"]')

    def clip_object(self, match):
        s = self.selenium
        s.click('xpath=//td[contains(string(.), "%s")]' % match)
        s.waitForElementPresent('css=div#bottomcontent > div')
        s.dragAndDropToObject(
            'xpath=//td[contains(string(.), "%s")]' % match,
            '//li[@uniqueid="Clip"]')
        s.pause(500)

    def create_teaserlist(self):
        self.open_centerpage()
        s = self.selenium
        s.click('link=*Add block*')
        s.waitForElementPresent('css=a.choose-block')
        s.click('//a[@class="choose-block"]')
        s.waitForElementPresent('css=div.block-types')
        s.click('link=List of teasers')
        s.waitForElementPresent('css=div.type-teaser')

    def test_adding_via_drag_and_drop_from_clipboard(self):
        self.open('/')
        s = self.selenium

        self.create_clip()
        s.clickAndWait('link=Dateiverwaltung')
        self.clip_object('testcontent')

        self.create_teaserlist()

        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/testcontent"]',
            'css=div.type-teaser')
        s.waitForElementPresent('css=div.supertitle')

    def test_delete(self):
        s = self.selenium
        # Create test content
        s.open('/@@create-cp-test-content')
        self.open('/')
        self.create_clip()
        s.clickAndWait('link=Dateiverwaltung')
        self.clip_object('c1')
        self.clip_object('c2')
        self.clip_object('c3')

        self.create_teaserlist()

        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c3"]',
            'css=div.type-teaser')
        s.waitForTextPresent('c3 teaser')
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c2"]',
            'css=div.type-teaser')
        s.waitForTextPresent('c2 teaser')
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c1"]',
            'css=div.type-teaser')
        s.waitForTextPresent('c1 teaser')

        s.click('link=Edit teaser list')
        s.waitForElementPresent('css=div.teaser-list-edit-box')

        s.verifyXpathCount(
            '//div[@id="lightbox"]//a[@class="delete-link"]', 3)
        s.click(
            '//div[@id="lightbox"]//li[contains(string(.), "c2 teaser")]/'
            'a[@class="delete-link"]')
        s.waitForElementPresent('css=.confirm-delete')
        s.click('css=.confirm-delete > a')
        s.waitForXpathCount(
            '//div[@id="lightbox"]//a[@class="delete-link"]', 2)

        # When closing the lightbox the c2 teaser goes away
        s.click('css=a.CloseButton')
        s.waitForTextNotPresent('c2 teaser')


class TestTeaserMosaic(Test):

    def test_sorting(self):
        self.open_centerpage()
        s = self.selenium
        # Create three teaser bars

        s.click('link=*Add teaser bar*')
        s.waitForXpathCount('//div[@class="block type-teaser-bar"]', 1)
        s.click('link=*Add teaser bar*')
        s.waitForXpathCount('//div[@class="block type-teaser-bar"]', 2)
        s.click('link=*Add teaser bar*')
        s.waitForXpathCount('//div[@class="block type-teaser-bar"]', 3)

        # Get the ids of the bars
        s.storeAttribute('//div[@class="block type-teaser-bar"][1]@id', 'bar1')
        s.storeAttribute('//div[@class="block type-teaser-bar"][2]@id', 'bar2')
        s.storeAttribute('//div[@class="block type-teaser-bar"][3]@id', 'bar3')

        # All bars have an equal height, drag 0.75 of the height.
        s.storeElementHeight('id=${bar1}', 'bar-height');
        s.storeEval("new Number(storedVars['bar-height']) * 0.75", "delta_y")


        # Drag bar1 below bar2
        s.dragAndDrop('css=#${bar1} > .block-inner > .edit > .dragger',
                      '0,${delta_y}')
        s.verifyAttribute(
            '//div[@class="block type-teaser-bar"][1]@id', '${bar2}')
        s.verifyAttribute(
            '//div[@class="block type-teaser-bar"][2]@id', '${bar1}')

        # Drag bar3 above bar1. When we move up, we have to move farther
        # because the drag handle is on the bottom of the bar.
        s.storeEval("new Number(storedVars['bar-height']) * 1.75", "delta_y")
        s.dragAndDrop('css=#${bar3} > .block-inner > .edit > .dragger',
                      '0,-${delta_y}')
        s.dragAndDrop('css=#${bar3} > .block-inner > .edit > .dragger',
                      '0,-${delta_y}')
        s.verifyAttribute(
            '//div[@class="block type-teaser-bar"][1]@id', '${bar3}')
        s.verifyAttribute(
            '//div[@class="block type-teaser-bar"][2]@id', '${bar2}')
        s.verifyAttribute(
            '//div[@class="block type-teaser-bar"][3]@id', '${bar1}')

        # Make sure the drag survives page reloads. First wait a little after
        # the last drag to let the server finish storing etc.
        s.pause(500)
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent('xpath=//div[@class="landing-zone"]')
        s.verifyAttribute(
            '//div[@class="block type-teaser-bar"][1]@id', '${bar3}')
        s.verifyAttribute(
            '//div[@class="block type-teaser-bar"][2]@id', '${bar2}')
        s.verifyAttribute(
            '//div[@class="block type-teaser-bar"][3]@id', '${bar1}')


class CreateTestContent(object):

    def __call__(self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        c1 = zeit.cms.testcontenttype.testcontenttype.TestContentType()
        c1.teaserTitle = c1.shortTeaserTitle = u'c1 teaser'
        repository['c1'] = c1
        c2 = zeit.cms.testcontenttype.testcontenttype.TestContentType()
        c2.teaserTitle = c2.shortTeaserTitle = u'c2 teaser'
        repository['c2'] = c2
        c3 = zeit.cms.testcontenttype.testcontenttype.TestContentType()
        c3.teaserTitle = c3.shortTeaserTitle = u'c3 teaser'
        repository['c3'] = c3
        return 'Done.'


