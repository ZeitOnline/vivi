# coding: utf8
import lovely.remotetask.interfaces
import lxml.cssselect
import transaction
import zeit.cms.repository.interfaces
import zeit.content.quiz.quiz
import zope.component


def css_path(css):
    return lxml.cssselect.CSSSelector(css).path


class TestDottedName(zeit.content.cp.testing.SeleniumTestCase):

    def test_lookup(self):
        self.open_centerpage()
        # Test a name that we know that exists
        # XXX should be moved to zeit.cms
        result = self.eval(
            'new (window.zeit.cms.resolveDottedName("zeit.edit.Editor"))')
        self.assertEquals('zeit.edit.Editor', result['__name__'])


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

        s.assertCssCount('css=#informatives .block a.delete-link', 3)
        s.click('css=#informatives .block a.delete-link')
        # mostread/mostcommented are still there
        s.waitForCssCount('css=#informatives .block a.delete-link', 2)

    def test_hover(self):
        self.create_teaserlist()
        s = self.selenium
        s.verifyElementNotPresent('css=.block.type-teaser.hover')
        s.mouseOver('css=div.teaser-list')
        s.pause(100)
        s.verifyElementPresent('css=.block.type-teaser.hover')
        s.mouseMoveAt('css=div.teaser-list', '100,100')
        s.pause(100)
        s.verifyElementNotPresent('css=.block.type-teaser.hover')

    def test_common_data_edit_form(self):
        self.create_teaserlist()
        s = self.selenium

        s.click('xpath=(//a[contains(@class, "edit-link")])[3]')
        # Wait for tab content to load, to be certain that the tabs have been
        # wired properly.
        s.waitForElementPresent('css=.layout-chooser')
        s.click('//a[@href="tab-1"]')
        s.waitForElementPresent('id=form.title')
        s.type('form.title', 'FooTitle')
        s.click('//div[@id="tab-1"]//input[@id="form.actions.apply"]')
        s.waitForElementNotPresent('css=a.CloseButton')

        s.click('xpath=(//a[contains(@class, "edit-link")])[3]')
        s.waitForElementPresent('css=.layout-chooser')
        s.click('//a[@href="tab-1"]')
        s.waitForElementPresent('form.title')
        s.waitForValue('form.title', 'FooTitle')


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

    def test_sort_teaser_contents(self):
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
        s.mouseDown(li('c3'))
        s.mouseMoveAt(li('c3'), '0,5')
        s.mouseMoveAt(li('c3'), '0,%s' % int(delta_y))
        s.mouseUp(li('c3'))

        s.waitForElementPresent('css=div.teaser-list-edit-box')
        s.waitForOrdered(li('c2', True), li('c1'))
        s.waitForOrdered(li('c1', True), li('c3'))

        # Drag the c1 node .75 up; the resulting order is 1, 2, 3
        delta_y = (height + height_landing) * -0.75
        s.mouseDown(li('c1'))
        s.mouseMoveAt(li('c1'), '0,5')
        s.mouseMoveAt(li('c1'), '0,%s' % int(delta_y))
        s.mouseUp(li('c1'))

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
        s.pause(500)
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
        s.assertCssCount('css=.lightbox li.landing-zone', 1)
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c1"]',
            'css=.lightbox .landing-zone', '10,10')
        s.waitForElementPresent('css=.lightbox li.edit-bar')

        # Now, there are two landing zones
        s.assertCssCount('css=.lightbox li.landing-zone', 2)
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c2"]',
            'css=.lightbox .landing-zone:first-child', '10,10')
        s.waitForCssCount('css=.lightbox li.edit-bar', 2)
        s.assertCssCount('css=.lightbox li.landing-zone', 3)

    def test_edit_box_url_input(self):
        self.create_teaserlist()
        s = self.selenium
        s.click('link=Edit teaser list')
        s.waitForElementPresent('css=.url-input input')
        s.type('css=.url-input input', 'http://xml.zeit.de/testcontent\n')
        s.waitForElementPresent('css=.lightbox li.edit-bar')
        s.assertCssCount('css=.lightbox li.landing-zone', 2)

    def test_toggle_visible(self):
        self.open_centerpage()
        s = self.selenium

        s.click('link=Struktur')
        teaser_module = self.get_module('cp', 'List of teasers')
        s.waitForElementPresent(teaser_module)
        s.dragAndDropToObject(
            teaser_module,
            'css=.landing-zone.action-cp-module-droppable', '10,10')
        s.waitForElementPresent(
            'css=.block.type-area .block.type-teaser')

        s.assertElementNotPresent('css=.block.type-teaser.block-visible-off')
        s.click('link=Switch visible')
        s.waitForElementPresent('css=.block.type-teaser.block-visible-off')
        s.click('link=Switch visible')
        s.waitForElementNotPresent('css=.block.type-teaser.block-visible-off')


class TestMoving(zeit.content.cp.testing.SeleniumTestCase):

    def setUp(self):
        super(TestMoving, self).setUp()
        cp = self.create_and_checkout_centerpage()
        self.teaser = zope.component.getAdapter(
            cp['lead'], zeit.edit.interfaces.IElementFactory, 'teaser')()
        transaction.commit()
        self.open_centerpage(create_cp=False)

    def test_move_block_between_areas(self):
        s = self.selenium
        s.dragAndDropToObject(
            'css=#lead .block.type-teaser .dragger',
            'css=#informatives .landing-zone.action-cp-module-movable',
            '10,10')
        s.waitForElementPresent('css=#informatives .block.type-teaser')

    def test_move_block_inside_area_to_change_order(self):
        selector = css_path('#informatives > .block-inner > .editable-module')
        path = 'xpath=' + selector + '[{pos}]@id'

        s = self.selenium
        block1 = s.getAttribute(path.format(pos=1))
        block2 = s.getAttribute(path.format(pos=2))
        s.dragAndDropToObject(
            'css=#{} .dragger'.format(block2),
            'css=#informatives .landing-zone.action-cp-module-movable',
            '10,10')
        s.waitForAttribute(path.format(pos=1), block2)
        s.waitForAttribute(path.format(pos=2), block1)

    def test_move_area_between_regions(self):
        s = self.selenium
        s.dragAndDropToObject(
            'css=#informatives .dragger',
            'css=#teaser-mosaic .landing-zone.action-cp-region-module-movable',
            '10,10')
        s.waitForElementPresent('css=#teaser-mosaic #informatives')

    def test_move_area_onto_body_creates_region_with_area(self):
        s = self.selenium
        s.assertElementPresent('css=#feature #informatives')
        s.dragAndDropToObject(
            'css=#feature #informatives .dragger',
            'css=#body .landing-zone.action-cp-region-module-movable',
            '10,10')
        s.waitForElementNotPresent('css=#feature #informatives')
        # inserted area on top, thus created region is first region
        s.assertElementPresent('css=#body > .type-region #informatives')

    def test_move_area_inside_region_to_change_order(self):
        selector = css_path('#feature > .block-inner > .type-area')
        path = 'xpath=' + selector + '[{pos}]@id'

        s = self.selenium
        area1 = s.getAttribute(path.format(pos=1))
        area2 = s.getAttribute(path.format(pos=2))
        s.dragAndDropToObject(
            'css=#{} .dragger'.format(area2),
            'css=#feature .landing-zone.action-cp-region-module-movable',
            '10,10')
        s.waitForAttribute(path.format(pos=1), area2)
        s.waitForAttribute(path.format(pos=2), area1)

    def test_move_regions_inside_body_to_change_order(self):
        path = 'xpath=' + css_path('#body > .type-region') + '[{pos}]@id'

        s = self.selenium
        s.verifyAttribute(path.format(pos=1), 'feature')
        s.verifyAttribute(path.format(pos=2), 'teaser-mosaic')
        s.dragAndDropToObject(
            'css=#teaser-mosaic .dragger',
            'css=#body .landing-zone.action-cp-type-region-movable',
            '10,10')
        s.waitForAttribute(path.format(pos=1), 'teaser-mosaic')
        s.waitForAttribute(path.format(pos=2), 'feature')


class TestLandingZone(zeit.content.cp.testing.SeleniumTestCase):

    def test_lead(self):
        self.create_content_and_fill_clipboard()
        self.open_centerpage()
        s = self.selenium

        s.verifyElementNotPresent('css=.block.type-teaser')
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c3"]',
            'css=.landing-zone.action-cp-module-droppable', '10,10')
        s.waitForElementPresent('css=.block.type-teaser')

    def test_zones_after_blocks(self):
        self.create_content_and_fill_clipboard()
        self.open_centerpage()
        s = self.selenium

        # Create a block, there will be a landing zone after it:
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c2"]', 'css=#lead .landing-zone', '10,10')
        s.verifyElementPresent('css=.block + .landing-zone')

        # The "normal" landing zone is also there
        s.verifyElementPresent('css=.landing-zone + .block')

        # Drop something on the after-block landing zone
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c1"]',
            'css=.block + .landing-zone', '10,10')
        s.waitForElementPresent('css=.block.type-teaser')


class TestVideoBlock(zeit.content.cp.testing.SeleniumTestCase):

    def create_videoblock(self):
        s = self.selenium
        s.click('link=Struktur')
        module = self.get_module('cp', 'Video')
        s.waitForElementPresent(module)
        s.dragAndDropToObject(
            module,
            'css=.landing-zone.action-cp-module-droppable', '10,10')
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
        s.click('link=Struktur')
        module = self.get_module('cp', 'Quiz')
        s.waitForElementPresent(module)
        s.dragAndDropToObject(
            module,
            'css=.landing-zone.action-cp-module-droppable', '10,10')
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
        s.click('link=Struktur')
        module = self.get_module('cp', 'XML')
        s.waitForElementPresent(module)
        s.dragAndDropToObject(
            module,
            'css=.landing-zone.action-cp-module-droppable', '10,10')
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
                'css=#lead .landing-zone', '10,10')
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
            s.waitForElementPresent('css=li.error')
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
            'css=.landing-zone.action-cp-module-droppable', '10,10')
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
        # We cannot use waitForText, since the DOM element changes in-between
        # but Selenium retrieves the element once and only checks the value
        # repeatedly, thus leading to an error that DOM is no longer attached.
        for i in range(10):
            try:
                s.assertText('//li[@uniqueid="Clip"]', '*c1-2*')
                break
            except:
                s.pause(100)
                continue
        s.assertText('//li[@uniqueid="Clip"]', '*c1-2*')

        # Verify text still in the drag source:
        s.verifyText('css=.teaser-list > .teaser', '*c1 teaser*')
