# coding: utf-8
import lxml.cssselect
import z3c.etestbrowser.testing
import zeit.cms.testing
import zeit.content.cp.browser.testing
import zeit.content.cp.testing


class ElementTestHelper(object):
    """Helper class to test creation and deletion of IRegion and IArea"""

    name = NotImplemented

    def setUp(self):
        super(ElementTestHelper, self).setUp()
        self.open_centerpage()

    def test_add_element_creates_new_element(self):
        s = self.selenium
        s.assertCssCount('css=.type-{}'.format(self.name), 2)
        self.make_one()
        s.waitForCssCount('css=.type-{}'.format(self.name), 3)

    def test_delete_element_removes_element(self):
        s = self.selenium
        s.assertCssCount('css=.type-{}'.format(self.name), 2)
        s.click('css=.type-{} > .block-inner > .edit-bar > .delete-link'
                .format(self.name))
        s.waitForConfirmation(u'Wirklich löschen?')
        s.waitForCssCount('css=.type-{}'.format(self.name), 1)


class RegionTest(
        ElementTestHelper,
        zeit.content.cp.testing.SeleniumTestCase):

    name = 'region'

    def make_one(self):
        self.selenium.click('link=*Add region*')


class AreaTest(
        ElementTestHelper,
        zeit.content.cp.testing.SeleniumTestCase):

    name = 'area'

    def make_one(self, parent_selector='.type-region'):
        selector = 'css={} .action-cp-region-module-droppable'.format(
            parent_selector)

        module = self.get_module('region', '1/1')
        self.selenium.click(u'link=Struktur')
        self.selenium.click(u'link=Flächen')
        self.selenium.waitForElementPresent(module)
        self.selenium.dragAndDropToObject(
            module, selector, '10,10')

    def test_add_area_in_body_creates_region_with_nested_area(self):
        s = self.selenium
        s.assertCssCount('css=.type-region', 2)
        s.assertCssCount('css=.type-area', 2)
        self.make_one(parent_selector='#body')
        s.waitForCssCount('css=.type-region', 3)
        s.waitForCssCount('css=.type-area', 3)


class ElementBrowserTestHelper(object):

    name = NotImplemented

    def setUp(self):
        super(ElementBrowserTestHelper, self).setUp()
        self.browser = z3c.etestbrowser.testing.ExtendedTestBrowser()
        self.browser.addHeader('Authorization', 'Basic user:userpw')
        self.browser.xml_strict = True
        zeit.content.cp.browser.testing.create_cp(self.browser)
        self.browser.open('contents')
        self.content_url = self.browser.url

    def get_edit_link(self, index=0):
        self.browser.open(self.content_url)
        return lxml.cssselect.CSSSelector(
            '.type-{} .edit-bar > .common-link'.format(
                self.name))(self.browser.etree)[index].get('href')

    def test_can_set_title(self):
        b = self.browser
        b.open(self.get_edit_link())
        b.getControl('Title').value = 'FooBarBaz'
        b.getControl('Apply').click()

        b.open(self.get_edit_link())
        self.assertEqual('FooBarBaz', b.getControl('Title').value)


class RegionBrowserTest(
        ElementBrowserTestHelper,
        zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.layer

    name = 'region'

    def make_one(self):
        self.browser.open(self.content_url)
        self.browser.getLink('Add region').click()


class AreaBrowserTest(
        ElementBrowserTestHelper,
        zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.layer

    name = 'area'

    def make_one(self):
        self.browser.open(self.content_url)
        self.browser.open(
            'feature/@@landing-zone-drop-module?block_type=area&order=top')

    def test_can_set_layout_for_area(self):
        b = self.browser
        edit_url = (
            'http://localhost/++skin++cms/workingcopy/zope.user/island/'
            'body/feature/{}/edit-properties'.format('lead'))
        b.open(edit_url)
        b.getLink('Ad-Medium Rectangle').click()
        b.open(edit_url)
        self.assertEllipsis('...<a ... class="mr selected"...', b.contents)


class TooltipFixture(object):

    def setUp(self):
        super(TooltipFixture, self).setUp()
        with zeit.cms.testing.site(self.getRootFolder()):
            self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()
            self.repository['data'] = zeit.cms.repository.folder.Folder()
            self.repository['data']['cp-area-schemas'] = \
                zeit.cms.repository.folder.Folder()

            first = zeit.cms.repository.file.LocalFile(mimeType='text/plain')
            with first.open('w') as file_:
                file_.write('1/3')
            self.repository['data']['cp-area-schemas']['1_3.svg'] = first

            second = zeit.cms.repository.file.LocalFile(mimeType='text/plain')
            with second.open('w') as file_:
                file_.write('2/3')
            self.repository['data']['cp-area-schemas']['2_3.svg'] = second


class TooltipBrowserTest(TooltipFixture, zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.layer

    def test_schematic_preview_returns_content_of_matched_files(self):
        self.browser.open(
            'http://localhost/++skin++vivi/repository/cp/@@checkout')
        self.browser.open('informatives/@@schematic-preview')
        self.assertEllipsis('...2/3...active...1/3...', self.browser.contents)


class TooltipSeleniumTest(
        TooltipFixture,
        zeit.content.cp.testing.SeleniumTestCase):

    def test_schematic_layout_of_areas_is_shown_in_tooltip(self):
        self.open('/repository/cp/@@checkout')
        s = self.selenium
        s.assertElementNotPresent('css=.schematic-preview-tooltip')
        s.mouseOver('css=#informatives > .block-inner > .edit-bar')
        s.waitForElementPresent('css=.schematic-preview-tooltip')


class OverflowSeleniumTest(zeit.content.cp.testing.SeleniumTestCase):

    def test_reloads_overflow_area(self):
        self.open_centerpage()
        s = self.selenium
        s.click('css=#lead .edit-bar .edit-link')
        # Wait for tab content to load, to be certain that the tabs have been
        # wired properly.
        s.waitForElementPresent('css=.layout-chooser')
        s.click('//a[@href="tab-3"]')
        s.waitForElementPresent('id=form.block_max')
        s.type('form.block_max', '1')
        s.select('form.overflow_into', '1/3 area no title')
        s.click(r'css=#tab-3 #form\.actions\.apply')
        s.waitForElementNotPresent('css=a.CloseButton')

        self.create_block('quiz', 'lead')
        self.create_block('teaser', 'lead')

        s.waitForElementPresent('css=#informatives .block.type-quiz')
