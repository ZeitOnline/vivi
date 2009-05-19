# coding: utf8
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import lxml.cssselect
import pkg_resources
import zeit.cms.browser.view
import zeit.cms.checkout.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.selenium
import zeit.cms.testcontenttype.testcontenttype
import zeit.content.cp.centerpage
import zope.component
import zeit.content.quiz.quiz


def css_path(css):
    return 'xpath=' + lxml.cssselect.CSSSelector(css).path


class Test(zeit.cms.selenium.Test):

    product_config = {
        'zeit.content.cp': {
            'rules-url': 'file://' + pkg_resources.resource_filename(
                'zeit.content.cp.tests', 'rule_testdata.py')
        }
    }

    def open_centerpage(self):
        s = self.selenium
        self.open('/@@create-test-cp')
        self.open('/workingcopy/zope.user/cp/@@cp-editor.html')
        s.waitForElementPresent('css=div.landing-zone')

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

    def create_content_and_fill_clipboard(self):
        s = self.selenium
        s.open('/@@create-cp-test-content')
        self.open('/')
        self.create_clip()
        s.clickAndWait('link=Dateiverwaltung')
        self.clip_object('c1')
        self.clip_object('c2')
        self.clip_object('c3')

    def create_filled_teaserlist(self):
        s = self.selenium
        self.create_content_and_fill_clipboard()
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


class TestDottedName(Test):

    def test_lookup(self):
        self.open_centerpage()
        s = self.selenium

        # Test a name that we know that exists
        s.verifyEval(
            'new (window.zeit.content.cp.resolveDottedName("zeit.content.cp.Editor"))',
            '[object Object]')


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
        link = 'css=div.block.type-teaser > * > div.edit > a.edit-link'
        s.waitForElementPresent(link)
        s.click(link)
        s.waitForElementPresent('form.actions.apply')
        s.click('form.actions.apply')
        s.waitForElementNotPresent('css=.lightbox')

        # Open delete verification
        s.pause(250)
        s.click('css=#cp-aufmacher a.delete-link')
        s.waitForElementPresent('css=div.confirm-delete')
        s.verifyElementPresent('css=div.block-inner.highlight')

        # Clicking anywhere else but on the remove confirmer, does close the
        # confirm but does not issue any action. Note that we've got to click
        # on the #confirm-delete-overlay which overlays everything.
        s.click("css=#confirm-delete-overlay")
        s.waitForElementNotPresent('css=div.confirm-delete')
        s.verifyElementNotPresent('css=div.block-inner.highlight')

        # Now really delete
        s.click('css=#cp-aufmacher a.delete-link')
        s.click('css=div.confirm-delete > a')
        s.waitForElementNotPresent('css=#cp-aufmacher a.delete-link')

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
        s.waitForXpathCount(css_path('a.choose-block'), 2)

    def test_hover(self):
        self.create_teaserlist()
        s = self.selenium

        # Hover mouse over block
        s.verifyElementNotPresent('css=div.block.hover')
        s.mouseOver('css=div.teaser-list')
        s.pause(100)
        s.verifyElementPresent('css=div.block.hover')
        s.mouseOut('css=div.teaser-list')
        s.pause(100)
        s.verifyElementNotPresent('css=div.block.hover')


    def test_common_data_edit_form(self):
        self.create_teaserlist()
        s = self.selenium

        s.click('css=a.edit-link')
        s.waitForElementPresent('id=tab-1')
        s.click('//a[@href="tab-1"]')
        s.waitForElementPresent('id=form.publisher')
        s.type('form.publisher', 'FooPublisher')
        s.click('//div[@id="tab-1"]//input[@id="form.actions.apply"]')
        s.waitForElementNotPresent('css=a.CloseButton')

        s.click('css=a.edit-link')
        s.waitForElementPresent('id=tab-1')
        s.click('//a[@href="tab-1"]')
        s.waitForValue('form.publisher', 'FooPublisher')


class TestTeaserBlock(Test):

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
        self.create_filled_teaserlist()

        s.click('link=Edit teaser list')
        s.waitForElementPresent('css=div.teaser-list-edit-box')

        s.verifyXpathCount(
            '//div[@class="lightbox"]//a[@class="delete-link"]', 3)
        s.click(
            '//div[@class="lightbox"]//li[contains(string(.), "c2 teaser")]/'
            'a[@class="delete-link"]')
        s.waitForElementPresent('css=.confirm-delete > a')
        s.click('css=.confirm-delete > a')
        s.waitForXpathCount(
            '//div[@class="lightbox"]//a[@class="delete-link"]', 2)

        # When closing the lightbox the c2 teaser goes away
        s.click('css=a.CloseButton')
        s.waitForTextNotPresent('c2 teaser')

    def test_sorting(self):
        s = self.selenium
        self.create_content_and_fill_clipboard()
        self.create_teaserlist()

        # Drag object to the teaser bar in "wrong order"
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c1"]',
            'css=div.type-teaser')
        s.waitForTextPresent('c1 teaser')
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c2"]',
            'css=div.type-teaser')
        s.waitForTextPresent('c2 teaser')
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c3"]',
            'css=div.type-teaser')
        s.waitForTextPresent('c3 teaser')

        # Edit the teaser list and reorder
        s.click('link=Edit teaser list')
        s.waitForElementPresent('css=div.teaser-list-edit-box')

        # Get the height of the first row and drag it 2.75 times the height so
        # it overlaps the third row. The initial order is 3, 2, 1. After drag
        # it is 2, 1, 3.
        def li(text, following_sibling=False):
            path = '//div[@class="lightbox"]//li[contains(string(.), "%s")]' % (
                text,)
            if following_sibling:
                path += '/following-sibling::li[1]'
            return path
        s.storeElementHeight(li('c3'), 'height')
        s.storeElementHeight(li('c3', True), 'height-landing')

        s.storeEval("(new Number(storedVars['height']) + "
                    "new Number(storedVars['height-landing'])) * 2.75",
                    'delta_y')
        s.dragAndDrop(li('c3'), '0,${delta_y}')

        s.waitForElementPresent('css=div.teaser-list-edit-box')
        s.waitForOrdered(li('c2', True), li('c1'))
        s.verifyOrdered(li('c1', True), li('c3'))

        # Drag the c1 node .75 up; the resulting order is 1, 2, 3
        s.storeEval("(new Number(storedVars['height']) + "
                    "new Number(storedVars['height-landing'])) * -0.75",
                    'delta_y')
        s.dragAndDrop(li('c1'), '0,${delta_y}')

        s.waitForElementPresent('css=div.teaser-list-edit-box')
        s.waitForOrdered(li('c1', True), li('c2'))
        s.verifyOrdered(li('c2', True), li('c3'))


    def test_inplace_teaser_editing_with_save(self):
        s = self.selenium
        self.create_filled_teaserlist()

        s.click('link=Edit teaser list')
        s.waitForElementPresent('css=div.teaser-list-edit-box')

        s.click(
            '//div[@class="lightbox"]//li[contains(string(.), "c2 teaser")]/'
            'a[contains(@class, "edit-link")]')
        s.waitForElementPresent('id=form.teaserTitle')

        # Changing the value and submitting the form will reload the teaser
        # list light box. The text will be in there then.
        s.type('id=form.teaserTitle', 'A nice new teaser')
        s.click('//form[contains(@action, "edit-teaser.html")]//input[@id="form.actions.apply"]')
        s.waitForTextPresent('A nice new teaser')

    def test_inplace_teaser_editing_with_abort(self):
        s = self.selenium
        self.create_filled_teaserlist()

        s.click('link=Edit teaser list')
        s.waitForElementPresent('css=div.teaser-list-edit-box')

        s.click(
            '//div[@class="lightbox"]//li[contains(string(.), "c2 teaser")]/'
            'a[contains(@class, "edit-link")]')
        s.waitForElementPresent('id=form.teaserTitle')

        # Closing the lightbox will remove the checked out object, thus remove
        # the lock. That means that we can edit again
        s.click('css=#cp-forms a.CloseButton')
        s.waitForElementNotPresent('css=#cp-forms a.CloseButton')
        s.click(
            '//div[@class="lightbox"]//li[contains(string(.), "c2 teaser")]/'
            'a[contains(@class, "edit-link")]')
        s.waitForElementPresent('id=form.teaserTitle')

    def test_edit_box_drop_of_content(self):
        self.create_content_and_fill_clipboard()
        self.create_teaserlist()
        s = self.selenium
        s.click('link=Edit teaser list')
        s.waitForElementPresent('css=.lightbox .landing-zone')

        # There is a landing zone
        s.verifyElementNotPresent('css=.lightbox li.edit-bar')
        s.verifyXpathCount(css_path('.lightbox li.landing-zone'), 1)
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c1"]',
            'css=.lightbox .landing-zone')
        s.waitForElementPresent('css=.lightbox li.edit-bar')

        # Now, there are two landing zones
        s.verifyXpathCount(css_path('.lightbox li.landing-zone'), 2)
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c2"]',
            'css=.lightbox .landing-zone:first-child')
        s.waitForXpathCount(css_path('.lightbox li.edit-bar'), 2)
        s.verifyXpathCount(css_path('.lightbox li.landing-zone'), 3)


class TestSorting(Test):

    def test_blocks_in_mosaic(self):
        self.open_centerpage()
        s = self.selenium

        s.click('link=*Add teaser bar*')

        path = css_path('.block.type-teaser-bar .block.type-teaser')

        for nr in range(4):
            s.waitForElementPresent('css=a.choose-block')
            s.click('//a[@class="choose-block"]')
            s.waitForElementPresent('css=div.block-types')
            s.click('link=List of teasers')
            s.waitForXpathCount(path, nr+1)

        # Get the ids of the blocks
        s.storeAttribute(path + '[1]@id', 'block1')
        s.storeAttribute(path + '[2]@id', 'block2')
        s.storeAttribute(path + '[3]@id', 'block3')
        s.storeAttribute(path + '[4]@id', 'block4')

        # All blocks have an equal width
        s.storeElementHeight('id=${block1}', 'width');

        # Drop block3 over block1
        s.storeEval("new Number(storedVars['width']) * -2.75", "delta_x")
        s.dragAndDrop('css=#${block3} > .block-inner > .edit > .dragger',
                      '${delta_x},0')
        s.pause(500)

        # 1 2 3 4 ->  3 1 2 4
        s.verifyOrdered('${block3}', '${block1}')
        s.verifyOrdered('${block1}', '${block2}')
        s.verifyOrdered('${block2}', '${block4}')


    def test_mosaic(self):
        self.open_centerpage()
        s = self.selenium
        # Create three teaser bars

        path = css_path('div.block.type-teaser-bar')
        s.click('link=*Add teaser bar*')
        s.waitForXpathCount(path, 1)
        s.click('link=*Add teaser bar*')
        s.waitForXpathCount(path, 2)
        s.click('link=*Add teaser bar*')
        s.waitForXpathCount(path, 3)

        # Get the ids of the bars
        s.storeAttribute(path + '[1]@id', 'bar1')
        s.storeAttribute(path + '[2]@id', 'bar2')
        s.storeAttribute(path + '[3]@id', 'bar3')

        # All bars have an equal height, drag 0.75 of the height.
        s.storeElementHeight('id=${bar1}', 'bar-height');
        s.storeEval("new Number(storedVars['bar-height']) * 0.75", "delta_y")


        # Drag bar1 below bar2: 1 2 3 -> 2 1 3
        s.dragAndDrop('css=#${bar1} > .block-inner > .edit > .dragger',
                      '0,${delta_y}')
        s.pause(500)
        s.verifyAttribute(path + '[1]@id', '${bar2}')
        s.verifyAttribute(path + '[2]@id', '${bar1}')

        # Drag bar3 above bar1. When we move up, we have to move farther
        # because the drag handle is on the bottom of the bar.
        # 2 1 3 -> 3 2 1
        s.storeEval("new Number(storedVars['bar-height']) * 2.75", "delta_y")
        s.dragAndDrop('css=#${bar3} > .block-inner > .edit > .dragger',
                      '0,-${delta_y}')
        s.pause(500)
        s.verifyAttribute(path + '[1]@id', '${bar3}')
        s.verifyAttribute(path + '[2]@id', '${bar2}')
        s.verifyAttribute(path + '[3]@id', '${bar1}')

        # Make sure the drag survives page reloads. 
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent('css=div.landing-zone')
        s.verifyAttribute(path + '[1]@id', '${bar3}')
        s.verifyAttribute(path + '[2]@id', '${bar2}')
        s.verifyAttribute(path + '[3]@id', '${bar1}')

    def test_lead(self):
        s = self.selenium

        self.create_teaserlist()
        s.storeAttribute('css=.block.type-teaser@id', 'block1')

        # Add a second teaser list
        s.click('link=*Add block*')
        s.waitForElementPresent('css=a.choose-block')
        s.click('//a[@class="choose-block"]')
        s.waitForElementPresent('css=div.block-types')
        s.click('link=List of teasers')
        s.waitForElementPresent(
            'css=.block.type-teaser + .landing-zone + .block.type-teaser')
        s.storeAttribute(
            'css=.block.type-teaser + .landing-zone + .block.type-teaser@id',
            'block2')

        s.storeElementHeight('id=${block2}', 'height');
        s.storeEval("new Number(storedVars['height']) * 1.75", "delta_y")

        s.dragAndDrop('css=#${block1} > .block-inner > .edit > .dragger',
                      '0,${delta_y}')
        s.waitForElementPresent(
            'css=.block.type-teaser + .landing-zone + .block.type-teaser')
        s.verifyAttribute(
            'css=.block.type-teaser + .landing-zone + .block.type-teaser@id',
            '${block1}')

    def test_informatives(self):
        s = self.selenium
        self.open_centerpage()

        # Add a teaser list
        s.click('css=#cp-informatives > * > .edit > a')
        s.waitForElementPresent('css=a.choose-block')
        s.click('//a[@class="choose-block"]')
        s.waitForElementPresent('css=div.block-types')
        s.click('link=List of teasers')
        s.waitForElementPresent('css=.block.type-teaser')
        s.storeAttribute('css=.block.type-teaser@id', 'block1')

        # Add a second teaser list
        s.click('css=#cp-informatives > * > .edit > a')
        s.waitForElementPresent('css=a.choose-block')
        s.click('//a[@class="choose-block"]')
        s.waitForElementPresent('css=div.block-types')
        s.click('link=List of teasers')
        s.waitForElementPresent(
            'css=.block.type-teaser + .block.type-teaser')
        s.storeAttribute(
            'css=.block.type-teaser + .block.type-teaser@id',
            'block2')

        s.storeElementHeight('id=${block2}', 'height');
        s.storeEval("new Number(storedVars['height']) * 1.75", "delta_y")

        s.dragAndDrop('css=#${block1} > .block-inner > .edit > .dragger',
                      '0,${delta_y}')
        s.waitForElementPresent(
            'css=.block.type-teaser + .block.type-teaser')
        s.verifyAttribute(
            'css=.block.type-teaser + .block.type-teaser@id',
            '${block1}')


class TestLandingZone(Test):

    def test_lead(self):
        self.create_content_and_fill_clipboard()
        self.open_centerpage()
        s = self.selenium

        s.verifyElementNotPresent('css=.block.type-teaser')
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c3"]',
            'css=.landing-zone')
        s.waitForElementPresent('css=.block.type-teaser')

    def test_zones_after_blocks(self):
        self.create_content_and_fill_clipboard()
        self.open_centerpage()
        s = self.selenium

        # Create a block, there will be a landing zone after it:
        s.click('link=*Add block*')
        s.waitForElementPresent('css=a.choose-block')
        s.verifyElementPresent('css=.block + .landing-zone')

        # The "normal" landing zone is also there
        s.verifyElementPresent('css=.landing-zone + .block')

        # Drop something
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c1"]',
            'css=.block + .landing-zone')
        s.waitForElementPresent('css=.block.type-teaser')


class TestVideoBlock(Test):

    def create_videoblock(self):
        s = self.selenium
        s.click('link=*Add block*')
        s.waitForElementPresent('css=a.choose-block')
        s.click('//a[@class="choose-block"]')
        s.waitForElementPresent('css=div.block-types')
        s.click('link=Videoblock')
        s.waitForElementPresent('css=div.type-videoblock')

    def test_lightbox_should_close_after_editing(self):
        self.open_centerpage()
        self.create_videoblock()
        s = self.selenium

        edit_link = 'css=div.block.type-videoblock > * > div.edit > a.edit-link'
        s.waitForElementPresent(edit_link)
        s.click(edit_link)
        s.waitForElementPresent('id=lightbox.form')
        s.pause(300)
        s.type('form.id', '12345')
        s.click('//input[@value="1W"]')
        s.select('form.format', 'small')
        s.click('form.actions.apply')
        s.waitForElementNotPresent('css=.lightbox')

        s.click('css=div.block.type-videoblock > * > div.edit > a.edit-link')
        s.waitForElementPresent('id=lightbox.form')
        s.click('form.actions.apply')
        s.waitForElementNotPresent('css=.lightbox')


class TestQuizBlock(Test):

    def create_quizblock(self):
        s = self.selenium
        s.click('link=*Add block*')
        s.waitForElementPresent('css=a.choose-block')
        s.click('//a[@class="choose-block"]')
        s.waitForElementPresent('css=div.block-types')
        s.click('link=Quizblock')
        s.waitForElementPresent('css=div.type-quizblock')

    def add_quiz(self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        quiz = zeit.content.quiz.quiz.Quiz()
        repository['my_quiz'] = quiz

    def test_add_quiz(self):
        self.open_centerpage()
        self.create_quizblock()
        self.add_quiz()

        s = self.selenium
        s.pause(300)
        s.click('css=div.type-quizblock > * > div.edit > a.edit-link')
        s.waitForElementPresent('id=lightbox.form')
        s.pause(100)
        s.type('css=input.object-reference', 'http://xml.zeit.de/my_quiz')
        s.click('form.actions.apply')
        s.waitForElementNotPresent('css=.lightbox')

        s.click('css=div.type-quizblock > * > div.edit > a.edit-link')
        s.waitForElementPresent('id=lightbox.form')
        s.waitForValue('css=input.object-reference',
                       'http://xml.zeit.de/my_quiz')
        s.click('form.actions.apply')
        s.waitForElementNotPresent('css=.lightbox')


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
        quiz = zeit.content.quiz.quiz.Quiz()
        quiz.teaserTitle = quiz.shortTeaserTitle = u'MyQuiz'
        repository['my_quiz'] = quiz
        return 'Done.'


class CreateTestCP(zeit.cms.browser.view.Base):

    def __call__(self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository['cp'] = zeit.content.cp.centerpage.CenterPage()
        cp = zeit.cms.checkout.interfaces.ICheckoutManager(
            repository['cp']).checkout()
        self.url(cp)
