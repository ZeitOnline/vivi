import time

import zeit.cms.testing


class TestPanels(zeit.cms.testing.SeleniumTestCase):
    layer = zeit.cms.testing.WEBDRIVER_LAYER

    def assertSidebarState(self, state):
        s = self.selenium
        s.waitForElementPresent('css=#sidebar-dragger.sidebar-%s' % state)

    def assertPanelState(self, id, state):
        s = self.selenium
        s.waitForElementPresent('css=#%s.panel.%s' % (id, state))
        time.sleep(0.25)

    def test_panels_should_be_foldable(self):
        s = self.selenium

        # Open a folder with articles.
        self.open('/repository/online/2007/01')

        self.assertPanelState('ClipboardPanel', 'unfolded')
        s.click('//div[@id = "ClipboardPanel"]/h1')
        self.assertPanelState('ClipboardPanel', 'folded')
        # Stays that way when reloading
        s.refresh()
        self.assertPanelState('ClipboardPanel', 'folded')

        # unfold again:
        s.click('//div[@id = "ClipboardPanel"]/h1')
        self.assertPanelState('ClipboardPanel', 'unfolded')
        # Stays that way when reloading
        s.refresh()
        self.assertPanelState('ClipboardPanel', 'unfolded')

    def test_sidebar_should_be_expandable_and_foldable(self):
        s = self.selenium
        self.open('/repository/online/2007/01')
        self.assertSidebarState('expanded')
        s.click('id=sidebar-dragger')
        self.assertSidebarState('folded')
        s.refresh()
        self.assertSidebarState('folded')
