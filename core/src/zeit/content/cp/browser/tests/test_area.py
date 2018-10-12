# coding: utf-8
import json
import lxml.cssselect
import unittest
import zeit.cms.testing
import zeit.content.cp.browser.testing
import zeit.content.cp.testing


class ElementTestHelper(object):
    """Helper class to test creation and deletion of IRegion and IArea"""

    name = NotImplemented
    starting_count = NotImplemented

    def setUp(self):
        super(ElementTestHelper, self).setUp()
        self.open_centerpage()

    def test_add_element_creates_new_element(self):
        s = self.selenium
        s.assertCssCount('css=.type-{}'.format(self.name), self.starting_count)
        self.make_one()
        s.waitForCssCount('css=.type-{}'.format(self.name),
                          self.starting_count + 1)

    def test_add_element_creates_element_of_given_kind(self):
        s = self.selenium
        locator = 'css=.type-{} .kind'.format(self.name)
        self.make_one(kind='Duo')
        s.waitForText(locator, 'Duo')

    def test_delete_element_removes_element(self):
        s = self.selenium
        s.assertCssCount('css=.type-{}'.format(self.name), self.starting_count)
        s.click('css=.type-{} > .block-inner > .edit-bar > .delete-link'
                .format(self.name))
        s.waitForConfirmation(u'Wirklich löschen?')
        s.waitForCssCount('css=.type-{}'.format(self.name),
                          self.starting_count - 1)

    def test_toggle_visible(self):
        self.test_add_element_creates_new_element()
        s = self.selenium
        visible_off_marker = 'css=.block.type-{}.block-visible-off'.format(
            self.name)
        s.assertElementNotPresent(visible_off_marker)
        toggle_visible = 'css=.block.type-{} .toggle-visible-link'.format(
            self.name)
        s.click(toggle_visible)
        s.waitForElementPresent(visible_off_marker)
        s.click(toggle_visible)
        s.waitForElementNotPresent(visible_off_marker)


class RegionTest(
        ElementTestHelper,
        zeit.content.cp.testing.SeleniumTestCase):

    name = 'region'
    starting_count = 1

    def make_one(self, kind='Empty'):
        selector = 'css=.action-cp-body-module-droppable'
        module = self.get_module('body', kind)
        self.selenium.click(u'link=Struktur')
        self.selenium.click(u'link=Regionen')
        self.selenium.waitForElementPresent(module)
        self.selenium.dragAndDropToObject(
            module, selector, '10,10')


class AreaTest(
        ElementTestHelper,
        zeit.content.cp.testing.SeleniumTestCase):

    name = 'area'
    starting_count = 2

    def make_one(self, parent_selector='.type-region', kind='Solo'):
        selector = 'css={} .action-cp-region-module-droppable'.format(
            parent_selector)

        module = self.get_module('region', kind)
        self.selenium.click(u'link=Struktur')
        self.selenium.click(u'link=Flächen')
        self.selenium.waitForElementPresent(module)
        self.selenium.dragAndDropToObject(
            module, selector, '10,10')


class ElementBrowserTestHelper(object):

    name = NotImplemented

    def setUp(self):
        super(ElementBrowserTestHelper, self).setUp()
        self.browser = zeit.cms.testing.Browser()
        self.browser.addHeader('Authorization', 'Basic user:userpw')
        zeit.content.cp.browser.testing.create_cp(self.browser)
        self.browser.open('contents')
        self.content_url = self.browser.url

    def get_edit_link(self, index=0):
        self.browser.open(self.content_url)
        document = lxml.etree.XML(self.browser.contents)
        return lxml.cssselect.CSSSelector(
            '.type-{} .edit-bar > .common-link'.format(self.name)
        )(document)[index].get('href')

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

    layer = zeit.content.cp.testing.ZCML_LAYER

    name = 'region'

    def make_one(self):
        self.browser.open(self.content_url)
        self.browser.open(
            'body/@@landing-zone-drop-module?block_type=region&order=top')


class AreaBrowserTest(
        ElementBrowserTestHelper,
        zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.ZCML_LAYER

    name = 'area'

    def make_one(self):
        self.browser.open(self.content_url)
        self.browser.open(
            'feature/@@landing-zone-drop-module?block_type=area&order=top')

    def get_edit_area_link(self, index=0):
        self.browser.open(self.content_url)
        document = lxml.etree.XML(self.browser.contents)
        return lxml.cssselect.CSSSelector(
            '.type-{} .edit-bar > .edit-link'.format(self.name)
        )(document)[index].get('href')

    def test_edit_form_stores_custom_query(self):
        b = self.browser
        b.open(self.get_edit_area_link())
        edit_url = b.url
        b.getControl(name='form.automatic_type').displayValue = [
            'automatic-area-type-query']
        b.getControl('Amount of teasers').value = '1'
        b.getControl('Add Custom Query').click()
        b.getControl('Custom Query Type').displayValue = ['query-type-serie']
        b.getControl('Add Custom Query').click()
        b.getControl('Custom Query Type', index=1).displayValue = [
            'query-type-ressort']
        b.getControl('Add Custom Query').click()
        b.getControl('Serie').displayValue = ['Autotest']
        b.getControl('Ressort').displayValue = ['Deutschland']
        b.getControl('Sub ressort').displayValue = ['Integration']
        b.getControl('Channel').displayValue = ['International']
        b.getControl('Subchannel').displayValue = ['Meinung']
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)

        b.open(edit_url)
        self.assertEqual(
            ['query-type-serie'],
            b.getControl('Custom Query Type', index=0).displayValue)
        self.assertEqual(
            ['query-type-ressort'],
            b.getControl('Custom Query Type', index=1).displayValue)
        self.assertEqual(
            ['query-type-channels'],
            b.getControl('Custom Query Type', index=2).displayValue)
        self.assertEqual(['Autotest'], b.getControl('Serie').displayValue)
        self.assertEqual(
            ['Deutschland'], b.getControl('Ressort').displayValue)
        self.assertEqual(
            ['Integration'], b.getControl('Sub ressort').displayValue)
        self.assertEqual(
            ['International'], b.getControl('Channel').displayValue)
        self.assertEqual(['Meinung'], b.getControl('Subchannel').displayValue)

    def test_removes_mismatched_custom_query_value_on_type_change(self):
        b = self.browser
        b.open(self.get_edit_area_link())
        b.getControl(name='form.automatic_type').displayValue = [
            'automatic-area-type-query']
        b.getControl('Amount of teasers').value = '1'
        b.getControl('Add Custom Query').click()
        b.getControl('Channel').displayValue = ['International']
        b.getControl('Custom Query Type').displayValue = [
            'query-type-authorships']
        b.getControl('Add Custom Query').click()  # Force a submit
        self.assertEqual(
            '', b.getControl(name='form.query.0..combination_02').value)


class TooltipFixture(object):

    def setUp(self):
        super(TooltipFixture, self).setUp()
        cp = zeit.content.cp.centerpage.CenterPage()
        cp['lead'].kind = u'major'
        cp['informatives'].kind = u'minor'
        self.repository['cp'] = cp
        self.repository['data'] = zeit.cms.repository.folder.Folder()
        self.repository['data']['cp-area-schemas'] = \
            zeit.cms.repository.folder.Folder()

        first = zeit.cms.repository.file.LocalFile(mimeType='text/plain')
        with first.open('w') as file_:
            file_.write('minor')
        self.repository['data']['cp-area-schemas']['minor.svg'] = first

        second = zeit.cms.repository.file.LocalFile(mimeType='text/plain')
        with second.open('w') as file_:
            file_.write('major')
        self.repository['data']['cp-area-schemas']['major.svg'] = second


class TooltipBrowserTest(TooltipFixture, zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.ZCML_LAYER

    def test_schematic_preview_returns_content_of_matched_files(self):
        self.browser.open(
            'http://localhost/++skin++vivi/repository/cp/@@checkout')
        self.browser.open('informatives/@@schematic-preview')
        self.assertEllipsis('...major...active...minor...',
                            self.browser.contents)


class TooltipSeleniumTest(
        TooltipFixture,
        zeit.content.cp.testing.SeleniumTestCase):

    @unittest.skip('Feature disabled')
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
        s.waitForElementPresent('css=.lightbox')
        s.click('//a[@href="tab-2"]')
        s.waitForElementPresent('id=form.block_max')
        s.type('form.block_max', '1')
        s.select('form.overflow_into', 'minor area no title')
        s.click(r'css=#tab-2 #form\.actions\.apply')
        s.click('css=a.CloseButton')
        s.waitForElementNotPresent('css=a.CloseButton')

        self.create_block('quiz', 'lead')
        self.create_block('teaser', 'lead')

        s.waitForElementPresent('css=#informatives .block.type-quiz')


class ConfiguredRegionTest(zeit.content.cp.testing.SeleniumTestCase):

    def make_one(self):
        s = self.selenium
        s.click(u'link=Struktur')
        s.click(u'link=Regionen')
        module = self.get_module('body', 'Duo')
        s.waitForElementPresent(module)
        s.dragAndDropToObject(
            module, 'css=.action-cp-body-module-droppable', '10,10')
        s.waitForCssCount('css=.type-region', 2)

    def test_drop_configured_region_creates_nested_areas(self):
        s = self.selenium
        self.open_centerpage()
        count = s.getCssCount('css=.type-region')
        self.make_one()
        s.waitForCssCount('css=.type-region', count + 1)

    def test_creating_configured_region_sets_kind_on_region(self):
        self.open_centerpage()
        self.make_one()
        self.selenium.assertText('css=.type-region .kind', 'Duo')


class AreaConfigurationTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.ZCML_LAYER

    def setUp(self):
        super(AreaConfigurationTest, self).setUp()
        zeit.content.cp.browser.testing.create_cp(self.browser)
        self.browser.open('contents')

    def test_applies_additional_parameters_and_type_converts_them(self):
        self.browser.handleErrors = False
        params = {'kind': 'ranking', 'areas': [{
            'kind': 'ranking',
            'apply_teaser_layouts_automatically': 'true',
            'first_teaser_layout': 'leader-upright',
        }]}
        self.browser.open(
            'body/landing-zone-drop-module?order=top&block_type=region'
            '&block_params=%s' % json.dumps(params))
        cp = zeit.cms.interfaces.ICMSWCContent(
            'http://xml.zeit.de/online/2007/01/island')
        area = cp.body.values()[0].values()[0]
        self.assertEqual(True, area.apply_teaser_layouts_automatically)
        self.assertEqual(
            'leader-upright', area.first_teaser_layout.id)
