# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.edit.testing


class EditorJavascript(zeit.edit.testing.SeleniumTestCase):

    def setUp(self):
        super(EditorJavascript, self).setUp()
        self.open('/@@/zeit.edit.browser.tests.fixtures/editor.html')
        self.wait_for_condition('!zeit.edit.editor.busy')

    def test_reload_loads_external_scripts(self):
        self.eval('zeit.edit.editor.reload("myblock", "external.html")')
        self.wait_for_condition('zeit.edit.external')

    def test_reload_loads_inline_scripts(self):
        self.eval('zeit.edit.editor.reload("myblock", "inline.html")')
        self.wait_for_condition('zeit.edit.inline')
