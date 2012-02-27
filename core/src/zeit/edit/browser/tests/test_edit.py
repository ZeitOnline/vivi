# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.edit.testing


class EditorJavascript(zeit.edit.testing.SeleniumTestCase):

    def test_reload_loads_external_scripts(self):
        self.open('/@@/zeit.edit.browser.tests.fixtures/editor.html')
        self.wait_for_condition('!zeit.edit.editor.busy')
        self.eval('zeit.edit.editor.reload("myblock", "external.html")')
        self.wait_for_condition('zeit.edit.external')

    def test_reload_loads_inline_scripts(self):
        self.open('/@@/zeit.edit.browser.tests.fixtures/editor.html')
        self.wait_for_condition('!zeit.edit.editor.busy')
        self.eval('zeit.edit.editor.reload("myblock", "inline.html")')
        self.wait_for_condition('zeit.edit.inline')

    def test_reload_imports_style_sheets(self):
        self.open('/@@/zeit.edit.browser.tests.fixtures/editor.html')
        self.wait_for_condition('!zeit.edit.editor.busy')
        s = self.selenium
        self.eval('zeit.edit.editor.reload("myblock", "style.html")')
        s.waitForElementPresent('css=#myblock h3')
        s.waitForNotVisible('css=#myblock h3')

    def test_initial_editor_load_loads_js_and_css(self):
        self.open(
            '/@@/zeit.edit.browser.tests.fixtures/initial-load/editor.html')
        self.wait_for_condition('!zeit.edit.editor.busy')
        self.wait_for_condition('zeit.edit.inline')
        self.wait_for_condition('zeit.edit.external')
        s = self.selenium
        s.waitForElementPresent('css=#myblock h3')
        s.waitForNotVisible('css=#myblock h3')

    def test_reloading_sub_elements_should_not_change_scroll_position(self):
        self.open(
            '/@@/zeit.edit.browser.tests.fixtures/scroll-position/editor.html')
        self.wait_for_condition('!zeit.edit.editor.busy')

        self.eval('document.getElementById("marker").scrollIntoView()')
        # thanks to
        # <http://www.snook.ca/archives/javascript/offsets_scrolling_overflow/>
        before = self.eval(
            'document.getElementById("cp-content-inner").scrollTop')
        self.eval(
            'window.MochiKit.Signal.signal('
            'zeit.edit.editor, "reload", "myblock", "empty.html")')
        self.wait_for_condition('!zeit.edit.editor.busy')
        after = self.eval(
            'document.getElementById("cp-content-inner").scrollTop')
        self.assertEqual(before, after)
