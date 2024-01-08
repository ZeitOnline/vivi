# coding: utf8
import unittest

from gocept.selenium.wd_selenese import split_locator
import lxml.cssselect
import transaction
import zope.app.appsetup.product
import zope.component

import zeit.content.cp.testing
import zeit.edit.interfaces


def css_path(css):
    return lxml.cssselect.CSSSelector(css).path


class TestDottedName(zeit.content.cp.testing.SeleniumTestCase):
    def test_lookup(self):
        self.open_centerpage()
        # Test a name that we know that exists
        # XXX should be moved to zeit.cms
        result = self.eval('new (window.zeit.cms.resolveDottedName("zeit.edit.Editor"))')
        self.assertEqual('zeit.edit.Editor', result['__name__'])


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
        s.waitForElementPresent('css=a.CloseButton')
        s.click('css=a.CloseButton')
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
        s.waitForElementPresent('css=a.CloseButton')
        s.click('css=a.CloseButton')
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

        s.dragAndDropToObject('//li[@uniqueid="Clip/testcontent"]', 'css=div.type-teaser')
        s.waitForElementPresent('css=div.supertitle')

    def test_delete_content(self):
        s = self.selenium
        self.create_content_and_fill_clipboard()
        self.create_teaserlist()
        s.dragAndDropToObject('//li[@uniqueid="Clip/c1"]', 'css=div.type-teaser', '10,150')
        s.waitForElementPresent('//div[@class="teaserTitle" and text() = "c1 teaser"]')

        s.click('css=.type-teaser a.common-link')
        s.waitForElementPresent('css=.edit-common-box')
        s.waitForElementPresent('css=.object-details')
        s.mouseMove('css=.object-details')
        s.click('css=a[rel=remove]')
        s.click('id=form.actions.apply')

        s.click('css=a.CloseButton')
        s.waitForElementNotPresent('//div[@class="teaserTitle" and text() = "c1 teaser"]')

    def test_toggle_visible(self):
        self.open_centerpage()
        s = self.selenium

        s.click('link=Struktur')
        teaser_module = self.get_module('cp', 'Teaser')
        s.waitForElementPresent(teaser_module)
        s.dragAndDropToObject(
            teaser_module, 'css=.landing-zone.action-cp-module-droppable', '10,10'
        )
        s.waitForElementPresent('css=.block.type-area .block.type-teaser')

        visible_off_marker = 'css=.block.type-teaser.block-visible-off'
        toggle_visible = 'css=.block.type-teaser .toggle-visible-link'
        s.assertElementNotPresent(visible_off_marker)
        s.click(toggle_visible)
        s.waitForElementPresent(visible_off_marker)
        s.click(toggle_visible)
        s.waitForElementNotPresent(visible_off_marker)


class TestMoving(zeit.content.cp.testing.SeleniumTestCase):
    def setUp(self):
        super().setUp()
        cp = self.create_and_checkout_centerpage()
        self.teaser = zope.component.getAdapter(
            cp['lead'], zeit.edit.interfaces.IElementFactory, 'teaser'
        )()
        transaction.commit()
        self.open_centerpage(create_cp=False)

    # Dragging down first activates, then deactivates the landing zone inside
    # #lead. On deactivate, the underlying content snaps upwards, thus causing
    # the landing zone in #informatives that we want to hit to move *above*
    # where the mouse cursor is right then. We'd have to simulate some
    # complicated mouse movement of "down and then up again" to hit the target.
    @unittest.skip('Quite impossible to do drag&drop in a way that works')
    def test_move_block_between_areas(self):
        s = self.selenium
        s.dragAndDropToObject(
            'css=#lead .block.type-teaser .dragger',
            'css=#informatives .landing-zone.action-cp-module-movable',
            '10,10',
        )
        s.waitForElementNotPresent('css=#lead .block.type-teaser')
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
            '10,10',
        )
        s.waitForAttribute(path.format(pos=1), block2)
        s.waitForAttribute(path.format(pos=2), block1)

    def test_move_area_between_regions(self):
        s = self.selenium
        s.click('link=Struktur')
        s.click('link=Regionen')
        module = self.get_module('body', 'Solo')
        s.waitForElementPresent(module)
        s.dragAndDropToObject(module, 'css=.action-cp-body-module-droppable', '10,10')
        s.waitForCssCount('css=.type-region', 2)
        region = s.selenium.find_elements(*split_locator('css=.type-region'))
        region = [x.get_attribute('id') for x in region]
        region = [x for x in region if x != 'feature'][0]
        s.dragAndDropToObject(
            'css=#feature #informatives .dragger',
            'css=#%s .landing-zone.action-cp-region-module-movable' % region,
            '10,10',
        )
        s.waitForElementNotPresent('css=#feature #informatives')
        s.waitForElementPresent('css=#%s #informatives' % region)

    def test_move_area_inside_region_to_change_order(self):
        selector = css_path('#feature > .block-inner > .type-area')
        path = 'xpath=' + selector + '[{pos}]@id'

        s = self.selenium
        area1 = s.getAttribute(path.format(pos=1))
        area2 = s.getAttribute(path.format(pos=2))
        s.dragAndDropToObject(
            'css=#{} .dragger'.format(area2),
            'css=#feature .landing-zone.action-cp-region-module-movable',
            '10,10',
        )
        s.waitForAttribute(path.format(pos=1), area2)
        s.waitForAttribute(path.format(pos=2), area1)

    def test_move_regions_inside_body_to_change_order(self):
        path = 'xpath=' + css_path('#body > .type-region') + '[{pos}]@id'

        s = self.selenium
        # create new regions since browser view of Jenkins is too small to move
        # existing regions with areas and blocks inside
        s.assertCssCount('css=.type-region', 1)
        selector = 'css=.action-cp-body-module-droppable'
        module = self.get_module('body', 'Empty')
        self.selenium.click('link=Struktur')
        self.selenium.click('link=Regionen')
        self.selenium.waitForElementPresent(module)
        self.selenium.dragAndDropToObject(module, selector, '10,10')
        s.waitForCssCount('css=.type-region', 2)
        self.selenium.dragAndDropToObject(module, selector, '10,10')
        s.waitForCssCount('css=.type-region', 3)

        region1 = s.getAttribute(path.format(pos=1))
        region2 = s.getAttribute(path.format(pos=2))
        s.dragAndDropToObject(
            'css=#{} .dragger'.format(region2),
            'css=#body .landing-zone.action-cp-type-region-movable',
            '10,10',
        )
        s.waitForAttribute(path.format(pos=1), region2)
        s.waitForAttribute(path.format(pos=2), region1)

    def test_move_area_integration_test(self):
        """Chain several actions to ensure that client side JS does not break.

        We often ran into issues caused by JS errors which cannot be discovered
        when testing actions one by one, since the first action might succeed
        and following actions might fail due to the JS error. Thus we need a
        test that chains several actions.

        """
        self.test_move_block_between_areas()
        self.test_move_block_inside_area_to_change_order()


class TestLandingZone(zeit.content.cp.testing.SeleniumTestCase):
    def test_lead(self):
        self.create_content_and_fill_clipboard()
        self.open_centerpage()
        s = self.selenium

        s.verifyElementNotPresent('css=.block.type-teaser')
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c3"]', 'css=.landing-zone.action-cp-module-droppable', '10,10'
        )
        s.waitForElementPresent('css=.block.type-teaser')

    def test_zones_after_blocks(self):
        self.create_content_and_fill_clipboard()
        self.open_centerpage()
        s = self.selenium

        # Create a block, there will be a landing zone after it:
        s.dragAndDropToObject('//li[@uniqueid="Clip/c2"]', 'css=#lead .landing-zone', '10,10')
        s.verifyElementPresent('css=.block + .landing-zone')

        # The "normal" landing zone is also there
        s.verifyElementPresent('css=.landing-zone + .block')

        # Drop something on the after-block landing zone
        s.dragAndDropToObject('//li[@uniqueid="Clip/c1"]', 'css=.block + .landing-zone', '10,10')
        s.waitForElementPresent('css=.block.type-teaser')


class TestQuizBlock(zeit.content.cp.testing.SeleniumTestCase):
    def test_add_quiz(self):
        self.open_centerpage()

        s = self.selenium
        s.click('link=Struktur')
        module = self.get_module('cp', 'Quiz')
        s.waitForElementPresent(module)
        s.dragAndDropToObject(module, 'css=.landing-zone.action-cp-module-droppable', '10,10')
        s.waitForElementPresent('css=div.type-quiz')


class TestXMLBlock(zeit.content.cp.testing.SeleniumTestCase):
    def test_add_xml_to_lead(self):
        self.open_centerpage()

        s = self.selenium
        s.click('link=Struktur')
        module = self.get_module('cp', 'XML')
        s.waitForElementPresent(module)
        s.dragAndDropToObject(module, 'css=.landing-zone.action-cp-module-droppable', '10,10')
        s.waitForElementPresent('css=div.type-xml')


class TestSidebar(zeit.content.cp.testing.SeleniumTestCase):
    def test_sidebar_should_be_folded_away(self):
        s = self.selenium
        self.open_centerpage()
        s.waitForElementPresent('//div[@id="sidebar-dragger" and @class="sidebar-expanded"]')


class TestOneClickPublish(zeit.content.cp.testing.SeleniumTestCase):
    def setUp(self):
        super().setUp()
        self.create_content_and_fill_clipboard()

    def _fill_lead(self):
        s = self.selenium
        for i in range(1, 4):
            s.dragAndDropToObject(
                '//li[@uniqueid="Clip/c%s"]' % i, 'css=#lead .landing-zone', '10,150'
            )
            s.waitForElementPresent('//div[@class="teaserTitle" and text() = "c%s teaser"]' % i)

    def test_editor_should_be_reloaded_after_publishing(self):
        s = self.selenium
        self.open_centerpage()
        # satisfy the rules and publish
        self._fill_lead()
        s.click('xpath=//a[@title="Publish"]')
        s.waitForElementPresent('css=div.lightbox')
        s.waitForPageToLoad()
        s.waitForElementPresent('css=div.landing-zone')
