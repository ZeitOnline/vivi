import zeit.edit.testing


class RestoreFolding(zeit.edit.testing.SeleniumTestCase):
    def test_ids_unknown_to_session_keep_their_initial_folding_state(self):
        self.open('/@@/zeit.edit.browser.tests.fixtures/fold.html')
        self.execute('zeit.edit.restore_folding();')
        s = self.selenium
        s.assertElementNotPresent('css=#foo.folded')
        s.assertElementPresent('css=#bar.folded')

    def test_folding_state_is_restored(self):
        self.open('/@@/zeit.edit.browser.tests.fixtures/fold.html')
        self.execute('zeit.edit.toggle_folded("foo");')
        self.execute('zeit.edit.toggle_folded("bar");')
        self.open('/@@/zeit.edit.browser.tests.fixtures/fold.html')
        self.execute('zeit.edit.restore_folding();')
        s = self.selenium
        s.assertElementPresent('css=#foo.folded')
        s.assertElementNotPresent('css=#bar.folded')
