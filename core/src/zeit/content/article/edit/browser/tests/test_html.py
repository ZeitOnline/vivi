# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.article.testing


class HTMLConvertTest(
    zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(HTMLConvertTest, self).setUp()
        self.add_article()

    def convert(self):
        self.selenium.getEval(
            "window.zeit.content.article.html.to_xml("
            "this.browserbot.findElement('css=.editable'))")

    def test_h3_is_translated_to_intertitle(self):
        s = self.selenium
        self.create('<h3>foo</h3>')
        self.convert()
        s.assertElementPresent('css=.editable intertitle:contains(foo)')
