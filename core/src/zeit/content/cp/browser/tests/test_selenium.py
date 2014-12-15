# coding: utf8
# Copyright (c) 2009-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import lovely.remotetask.interfaces
import lxml.cssselect
import zeit.cms.repository.interfaces
import zeit.content.quiz.quiz
import zope.component


def css_path(css):
    return lxml.cssselect.CSSSelector(css).path


class TestDottedName(zeit.content.cp.testing.SeleniumTestCase):

    def test_lookup(self):
        self.open_centerpage()
        s = self.selenium

        # Test a name that we know that exists
        # XXX should be moved to zeit.cms
        s.verifyEval(
            'new (window.zeit.cms.resolveDottedName("zeit.edit.Editor"))',
            '[object Object]')


class TestGenericEditing(zeit.content.cp.testing.SeleniumTestCase):

    def test_add_and_delete(self):
        self.create_teaserlist()
        s = self.selenium
        link = 'css=div.block.type-teaser > * > div.edit > a.edit-link'
        s.waitForElementPresent(link)
        s.click(link)
        # Wait for tab content to load, to be certain that the tabs have been
        # wired properly.
        s.waitForElementPresent('css=.layout-chooser')
        s.click('//a[@href="tab-1"]')
        apply_button = r'css=#tab-1 #form\.actions\.apply'
        s.waitForElementPresent(apply_button)
        s.click(apply_button)
        s.waitForElementNotPresent('css=.lightbox')

        s.verifyXpathCount(css_path('#informatives .block a.delete-link'), 3)
        s.chooseOkOnNextConfirmation()
        s.click('css=#informatives .block a.delete-link')
        s.waitForConfirmation(u'Wirklich löschen?')
        # mostread/mostcommented are still there
        s.waitForXpathCount(
            css_path('#informatives .block a.delete-link'), 2)

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

        s.click('xpath=(//a[contains(@class, "edit-link")])[3]')
        # Wait for tab content to load, to be certain that the tabs have been
        # wired properly.
        s.waitForElementPresent('css=.layout-chooser')
        s.click('//a[@href="tab-1"]')
        s.waitForElementPresent('id=form.publisher')
        s.type('form.publisher', 'FooPublisher')
        s.click('//div[@id="tab-1"]//input[@id="form.actions.apply"]')
        s.waitForElementNotPresent('css=a.CloseButton')

        s.click('xpath=(//a[contains(@class, "edit-link")])[3]')
        s.waitForElementPresent('css=.layout-chooser')
        s.click('//a[@href="tab-1"]')
        s.waitForElementPresent('form.publisher')
        s.waitForValue('form.publisher', 'FooPublisher')


class TestTeaserBlock(zeit.content.cp.testing.SeleniumTestCase):

    def test_adding_via_drag_and_drop_from_clipboard(self):
        self.open('/')
        s = self.selenium

        self.create_clip()
        self.open('/repository')
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
            path = ('//div[@class="lightbox"]//li[contains(string(.), "%s")]' %
                    text)
            if following_sibling:
                path += '/following-sibling::li[1]'
            return path

        height = s.getElementHeight(li('c3'))
        height_landing = s.getElementHeight(li('c3', True))

        delta_y = (height + height_landing) * 2.75
        s.dragAndDrop(li('c3'), '0,%s' % delta_y)

        s.waitForElementPresent('css=div.teaser-list-edit-box')
        s.waitForOrdered(li('c2', True), li('c1'))
        s.waitForOrdered(li('c1', True), li('c3'))

        # Drag the c1 node .75 up; the resulting order is 1, 2, 3
        delta_y = (height + height_landing) * -0.75
        s.dragAndDrop(li('c1'), '0,%s' % delta_y)

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
        s.click('//form[contains(@action, "edit-teaser.html")]'
                '//input[@id="form.actions.apply_in_article"]')
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

    def test_toggle_visible(self):
        self.open_centerpage()
        s = self.selenium

        s.click('link=Module')
        teaser_module = self.get_module('cp', 'List of teasers')
        s.waitForElementPresent(teaser_module)
        s.dragAndDropToObject(
            teaser_module,
            'css=.landing-zone.action-cp-module-droppable')
        s.waitForElementPresent(
            'css=.block.type-area .block.type-teaser')

        s.assertElementNotPresent('css=.block.type-teaser.block-visible-off')
        s.click('link=Switch visible')
        s.waitForElementPresent('css=.block.type-teaser.block-visible-off')
        s.click('link=Switch visible')
        s.waitForElementNotPresent('css=.block.type-teaser.block-visible-off')


class TestSorting(zeit.content.cp.testing.SeleniumTestCase):

    def test_sort_areas_inside_region(self):
        self.open_centerpage()
        s = self.selenium

        # Create three teaser bars
        path = css_path('div.block.type-area')

        self.selenium.click(u'link=Module')
        self.selenium.click(u'link=Flächen')

        module = self.get_module('region', '1/1')
        self.selenium.waitForElementPresent(module)

        self.selenium.dragAndDropToObject(
            module, 'css=.landing-zone.action-cp-region-module-droppable')
        s.waitForXpathCount(path, 3)
        self.selenium.dragAndDropToObject(
            module, 'css=.landing-zone.action-cp-region-module-droppable')
        s.waitForXpathCount(path, 4)
        self.selenium.dragAndDropToObject(
            module, 'css=.landing-zone.action-cp-region-module-droppable')
        s.waitForXpathCount(path, 5)

        path = 'xpath=' + path
        # Get the ids of the bars
        bar1 = s.getAttribute(path + '[3]@id')
        bar2 = s.getAttribute(path + '[4]@id')
        bar3 = s.getAttribute(path + '[5]@id')

        # All bars have an equal height
        bar_height = s.getElementHeight(bar1)
        delta_y = bar_height * 1.75

        # Drag bar1 below bar2: 1 2 3 -> 2 1 3
        s.dragAndDrop('css=#%s > .block-inner > .edit > .dragger' % bar1,
                      '0,%s' % delta_y)
        s.waitForAttribute(path + '[3]@id', bar2)
        s.verifyAttribute(path + '[4]@id', bar1)
        # Wait for JS to re-start sortables
        s.pause(400)

        # Drag bar3 to the first position.
        # 2 1 3 -> 3 2 1

        # XXX Selenium's drag&drop behaves strangely. It works better when the
        # target area is visible, but we don't really understand what's going
        # on here. :-(
        self.eval(
            'document.getElementById("%s").scrollIntoView(false);' % bar2)
        self.eval(
            'document.getElementById("cp-content-inner").scrollTop -= 50;')

        delta_y = -(bar_height * 2.75)
        s.dragAndDrop('css=#%s > .block-inner > .edit > .dragger' % bar3,
                      '0,%s' % delta_y)

        s.waitForAttribute(path + '[3]@id', bar3)
        s.verifyAttribute(path + '[4]@id', bar2)
        s.verifyAttribute(path + '[5]@id', bar1)

        # Make sure the drag survives page reloads.
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent('css=div.landing-zone')
        s.verifyAttribute(path + '[3]@id', bar3)
        s.verifyAttribute(path + '[4]@id', bar2)
        s.verifyAttribute(path + '[5]@id', bar1)

    def test_sort_blocks_inside_area(self):
        s = self.selenium

        self.create_content_and_fill_clipboard()
        self.open_centerpage()

        # Create a teaser list
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c2"]', 'css=#lead .landing-zone')
        s.waitForElementPresent('css=.block.type-teaser')
        block2 = s.getAttribute('css=.block.type-teaser@id')

        # Add a second teaser list
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c1"]', 'css=#lead .landing-zone')
        s.waitForElementPresent(
            'css=.block.type-teaser + .landing-zone + .block.type-teaser')
        block1 = s.getAttribute('css=.block.type-teaser@id')

        height = s.getElementHeight(block2)
        delta_y = height * 1.75

        # 1 2 -> 2 1
        s.dragAndDrop('css=#%s > .block-inner > .edit > .dragger' % block1,
                      '0,%s' % delta_y)
        s.waitForElementPresent(
            'css=.block.type-teaser + .landing-zone + .block.type-teaser')
        s.verifyAttribute(
            'css=.block.type-teaser + .landing-zone + .block.type-teaser@id',
            block1)


class TestLandingZone(zeit.content.cp.testing.SeleniumTestCase):

    def test_lead(self):
        self.create_content_and_fill_clipboard()
        self.open_centerpage()
        s = self.selenium

        s.verifyElementNotPresent('css=.block.type-teaser')
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c3"]',
            'css=.landing-zone.action-cp-module-droppable')
        s.waitForElementPresent('css=.block.type-teaser')

    def test_zones_after_blocks(self):
        self.create_content_and_fill_clipboard()
        self.open_centerpage()
        s = self.selenium

        # Create a block, there will be a landing zone after it:
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c2"]', 'css=#lead .landing-zone')
        s.verifyElementPresent('css=.block + .landing-zone')

        # The "normal" landing zone is also there
        s.verifyElementPresent('css=.landing-zone + .block')

        # Drop something on the after-block landing zone
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c1"]',
            'css=.block + .landing-zone')
        s.waitForElementPresent('css=.block.type-teaser')


class TestVideoBlock(zeit.content.cp.testing.SeleniumTestCase):

    def create_videoblock(self):
        s = self.selenium
        s.click('link=Module')
        module = self.get_module('cp', 'Video')
        s.waitForElementPresent(module)
        s.dragAndDropToObject(
            module,
            'css=.landing-zone.action-cp-module-droppable')
        s.waitForElementPresent('css=div.type-video')

    def test_lightbox_should_close_after_editing(self):
        self.open_centerpage()
        self.create_videoblock()
        s = self.selenium

        edit_link = 'css=div.block.type-video > * > div.edit > a.edit-link'
        s.waitForElementPresent(edit_link)
        s.click(edit_link)
        s.waitForElementPresent('id=lightbox.form')
        s.pause(300)
        s.type('form.id', '12345')
        s.click('//input[@value="1W"]')
        s.select('form.format', 'small')
        s.click('form.actions.apply')
        s.waitForElementNotPresent('css=.lightbox')

        s.click('css=div.block.type-video > * > div.edit > a.edit-link')
        s.waitForElementPresent('id=lightbox.form')
        s.click('form.actions.apply')
        s.waitForElementNotPresent('css=.lightbox')


class TestQuizBlock(zeit.content.cp.testing.SeleniumTestCase):

    def create_quizblock(self):
        s = self.selenium
        s.click('link=Module')
        module = self.get_module('cp', 'Quiz')
        s.waitForElementPresent(module)
        s.dragAndDropToObject(
            module,
            'css=.landing-zone.action-cp-module-droppable')
        s.waitForElementPresent('css=div.type-quiz')

    def add_quiz(self):
        with zeit.cms.testing.site(self.getRootFolder()):
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
        s.click('css=div.type-quiz > * > div.edit > a.edit-link')
        s.waitForElementPresent('id=lightbox.form')
        s.pause(100)
        s.type('css=input.object-reference', 'http://xml.zeit.de/my_quiz')
        s.click('form.actions.apply')
        s.waitForElementNotPresent('css=.lightbox')

        s.click('css=div.type-quiz > * > div.edit > a.edit-link')
        s.waitForElementPresent('id=lightbox.form')
        s.waitForValue('css=input.object-reference',
                       'http://xml.zeit.de/my_quiz')
        s.click('form.actions.apply')
        s.waitForElementNotPresent('css=.lightbox')


class TestXMLBlock(zeit.content.cp.testing.SeleniumTestCase):

    def test_add_xml_to_lead(self):
        self.open_centerpage()

        s = self.selenium
        s.click('link=Module')
        module = self.get_module('cp', 'XML')
        s.waitForElementPresent(module)
        s.dragAndDropToObject(
            module,
            'css=.landing-zone.action-cp-module-droppable')
        s.waitForElementPresent('css=div.type-xml')


class TestSidebar(zeit.content.cp.testing.SeleniumTestCase):

    def test_sidebar_should_be_folded_away(self):
        s = self.selenium
        self.open_centerpage()
        s.waitForElementPresent(
            '//div[@id="sidebar-dragger" and @class="sidebar-expanded"]')


class TestOneClickPublish(zeit.content.cp.testing.SeleniumTestCase):

    def setUp(self):
        super(TestOneClickPublish, self).setUp()
        with zeit.cms.testing.site(self.getRootFolder()):
            for name, task in zope.component.getUtilitiesFor(
                lovely.remotetask.interfaces.ITaskService):
                task.startProcessing()
        self.create_content_and_fill_clipboard()

    def tearDown(self):
        import threading
        with zeit.cms.testing.site(self.getRootFolder()):
            for name, task in zope.component.getUtilitiesFor(
                lovely.remotetask.interfaces.ITaskService):
                thread_name = task._threadName()
                task.stopProcessing()
                for thread in threading.enumerate():
                    if thread.getName() == thread_name:
                        thread.join()
                        break
        super(TestOneClickPublish, self).tearDown()

    def _fill_lead(self):
        s = self.selenium
        for i in range(1, 4):
            s.dragAndDropToObject(
                '//li[@uniqueid="Clip/c%s"]' % i,
                'css=#lead .landing-zone')
            s.waitForTextPresent('c%s teaser' % i)

    def test_publish_should_show_error_message(self):
        s = self.selenium
        self.open_centerpage()
        s.click('xpath=//a[@title="Publish"]')
        s.waitForElementPresent('css=div.lightbox')
        s.waitForElementPresent('publish.errors')
        s.verifyText('publish.errors',
                     'Cannot publish since validation rules are violated.')

    def test_editor_should_be_reloaded_after_publishing(self):
        s = self.selenium
        self.open_centerpage()
        # satisfy the rules and publish
        self._fill_lead()
        s.click('xpath=//a[@title="Publish"]')
        s.waitForElementPresent('css=div.lightbox')
        s.waitForPageToLoad()
        s.waitForElementPresent('css=div.landing-zone')

    def test_publish_failure_should_be_displayed(self):
        config = zope.app.appsetup.product._configs
        old_script = config['zeit.workflow']['publish-script']
        config['zeit.workflow']['publish-script'] = 'invalid'
        try:
            s = self.selenium
            self.open_centerpage()
            self._fill_lead()
            s.click('xpath=//a[@title="Publish"]')
            s.waitForElementPresent('css=div.lightbox')
            s.waitForPageToLoad()
            s.waitForElementPresent('css=div.landing-zone')
            s.verifyText('css=li.error',
                         'Error during publish/retract: OSError*')
        finally:
            config['zeit.workflow']['publish-script'] = old_script


class TestTeaserDragging(zeit.content.cp.testing.SeleniumTestCase):

    def test_source_removed_when_dropped_to_cp(self):
        self.create_filled_teaserlist()
        s = self.selenium
        s.dragAndDropToObject(
            'css=.teaser-list > .teaser',
            'css=.landing-zone.action-cp-module-droppable')
        s.waitForElementPresent(
            'css=#lead .block.type-teaser')
        s.verifyText('css=#lead .block.type-teaser .teaser-list',
                     '*c1 teaser*')
        s.verifyNotText('css=#lead .block.type-teaser .teaser-list',
                        '*c2 teaser*')
        # Verify the removal in the source:
        s.waitForNotText(
            'css=#informatives .block.type-teaser .teaser-list', '*c1 teaser*')

    def test_source_not_removed_when_not_dropped_to_cp(self):
        s = self.selenium
        self.create_filled_teaserlist()
        s.dragAndDropToObject(
            'css=.teaser-list > .teaser',
            '//li[@uniqueid="Clip"]')
        s.waitForText(
            '//li[@uniqueid="Clip"]', '*c1-2*')
        # Verify text still in the drag source:
        s.verifyText(
            'css=.teaser-list > .teaser', '*c1 teaser*')
