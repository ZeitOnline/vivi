# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.edit.testing


class EditorJavascript(zeit.edit.testing.SeleniumTestCase):

    def test_reload_loads_script_tags(self):
        s = self.selenium
        self.open('/@@/zeit.edit.browser.tests.fixtures/editor.html')
        foo = s.getEval('window.zeit.edit.editor')
