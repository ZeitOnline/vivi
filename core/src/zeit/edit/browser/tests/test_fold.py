import zeit.edit.testing


class RestoreFolding(zeit.edit.testing.SeleniumTestCase):

    def test_ids_unknown_to_session_keep_their_initial_folding_state(self):
        self.open('/@@/zeit.edit.browser.tests.fixtures/fold.html')
        self.eval('zeit.edit.restore_folding();')
        s = self.selenium
        s.assertElementNotPresent('css=#foo.folded')
        s.assertElementPresent('css=#bar.folded')

    def test_folding_state_is_restored(self):
        self.open('/@@/zeit.edit.browser.tests.fixtures/fold.html')
        self.eval('zeit.edit.toggle_folded("foo");')
        self.eval('zeit.edit.toggle_folded("bar");')
        self.open('/@@/zeit.edit.browser.tests.fixtures/fold.html')
        self.eval('zeit.edit.restore_folding();')
        s = self.selenium
        s.assertElementPresent('css=#foo.folded')
        s.assertElementNotPresent('css=#bar.folded')

    def test_folding_state_is_stored_per_context_url(self):
        self.open('/@@/zeit.edit.browser.tests.fixtures/fold.html')
        self.eval('zeit.edit.toggle_folded("foo");')
        self.open('/@@/zeit.edit.browser.tests.fixtures/fold.html')
        self.eval('window.context_url = "changed";')
        self.eval('zeit.edit.restore_folding();')
        s = self.selenium
        s.assertElementNotPresent('css=#foo.folded')
