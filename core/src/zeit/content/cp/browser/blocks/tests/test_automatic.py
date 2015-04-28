import transaction
import zeit.cms.checkout.interfaces
import zeit.content.cp.testing


class TestAutomaticTeaserBlock(zeit.content.cp.testing.SeleniumTestCase):

    def setUp(self):
        super(TestAutomaticTeaserBlock, self).setUp()
        self.auto_teaser_title = 'Teaser Title Foo'
        teaser = self.create_content('t1', self.auto_teaser_title)

        cp_with_teaser = self.create_and_checkout_centerpage(
            'cp_with_teaser', contents=[teaser])
        zeit.cms.checkout.interfaces.ICheckinManager(cp_with_teaser).checkin()

        self.cp = self.create_and_checkout_centerpage('cp')
        self.area = self.cp['feature'].create_item('area')
        self.area.referenced_cp = self.repository['cp_with_teaser']
        self.area.count = 1
        self.area.automatic = True
        self.area.automatic_type = 'centerpage'

        transaction.commit()
        self.open_centerpage(create_cp=False)

    def test_fill_automatic_areas_with_teaser(self):
        self.selenium.waitForTextPresent(self.auto_teaser_title)

    def test_toggle_visible_reloads_teaser(self):
        sel = self.selenium
        sel.assertCssCount('css=.block-visible-off', 0)
        sel.assertTextPresent(self.auto_teaser_title)

        sel.click('css=.block.type-auto-teaser .toggle-visible-link')
        sel.waitForCssCount('css=.block-visible-off', 1)
        sel.assertTextPresent(self.auto_teaser_title)

        sel.click('css=.block.type-auto-teaser .toggle-visible-link')
        sel.waitForCssCount('css=.block-visible-off', 0)
        sel.assertTextPresent(self.auto_teaser_title)

    def test_change_layout_reloads_teaser(self):
        sel = self.selenium
        sel.assertTextPresent(self.auto_teaser_title)
        sel.click('css=.block.type-auto-teaser .edit-link')
        sel.waitForElementPresent('css=.lightbox')
        sel.click('css=.two-side-by-side')
        sel.waitForElementPresent('css=.teaser-contents.two-side-by-side')
        sel.assertTextPresent(self.auto_teaser_title)

    def test_change_common_property_reloads_teaser(self):
        sel = self.selenium
        sel.assertTextPresent(self.auto_teaser_title)
        sel.assertCssCount('css=.block-visible-off', 0)

        sel.click('css=.block.type-auto-teaser .edit-link')
        sel.waitForElementPresent('css=.lightbox')
        sel.click('//a[@href="tab-1"]')
        sel.waitForElementPresent('id=form.visible')
        sel.check('id=form.visible')
        sel.click(r'css=#tab-1 #form\.actions\.apply')

        sel.waitForCssCount('css=.block-visible-off', 1)
        sel.assertTextPresent(self.auto_teaser_title)
