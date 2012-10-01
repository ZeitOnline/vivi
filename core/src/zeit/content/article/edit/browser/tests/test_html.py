# coding: utf-8
# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.article.edit.browser.testing


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

    def test_div_is_translated_to_p(self):
        s = self.selenium
        self.create('<div>foo</div>')
        self.convert()
        s.assertElementPresent('css=.editable p:contains(foo)')

    def test_b_is_translated_to_strong(self):
        s = self.selenium
        self.create('<p><b>foo</b></p>')
        self.convert()
        s.assertElementPresent('css=.editable p strong:contains(foo)')

    def test_i_is_translated_to_em(self):
        s = self.selenium
        self.create('<p><i>foo</i></p>')
        self.convert()
        s.assertElementPresent('css=.editable p em:contains(foo)')

    def test_double_p_is_removed(self):
        s = self.selenium
        self.create('<p><p>foo</p>')
        self.convert()
        s.assertElementPresent('css=.editable p:contains(foo)')
        s.assertXpathCount('//*[@class="editable"]//p', 1)

    def test_double_br_is_translated_to_p(self):
        s = self.selenium
        self.create('<p>foo<br><br>bar</p>')
        self.convert()
        s.assertElementPresent('css=.editable p p:contains(bar)')
        s.assertXpathCount('//*[@class="editable"]//br', 0)

    def test_a_witout_href_should_be_escaped(self):
        s = self.selenium
        self.create('<p>A stupid <a>link</a>.</p>')
        self.convert()
        s.assertAttribute('css=.editable p a@href', '#')

    def test_a_with_href_should_be_allowed(self):
        s = self.selenium
        self.create('<p>A working <a href="foo">link</a>.</p>')
        self.convert()
        s.assertAttribute('css=.editable p a@href', 'foo')

    def test_a_target_should_be_allowed(self):
        s = self.selenium
        self.create('<p>A working <a href="foo" target="_blank">link</a>.</p>')
        self.convert()
        s.assertAttribute('css=.editable p a@target', '_blank')

    def test_text_nodes_should_become_paragraphs(self):
        s = self.selenium
        self.create('Mary<p>had a little</p>')
        self.convert()
        s.assertElementPresent('css=.editable p:contains(Mary)')

    def test_top_level_inline_styles_are_joined_to_paragraph(self):
        s = self.selenium
        self.create('Mary <strong>had</strong> a little lamb.')
        self.convert()
        s.assertElementPresent('css=.editable p:contains(Mary had a)')
        s.assertElementPresent('css=.editable p > strong:contains(had)')

    def test_top_level_inline_styles_are_not_joined_to_existing_p(self):
        s = self.selenium
        self.create(
            '<p>foo</p>Mary <strong>had</strong> a little lamb. <p>bar</p>')
        self.convert()
        s.assertElementPresent('css=.editable p:contains(Mary had a)')
        s.assertElementPresent('css=.editable p > strong:contains(had)')
        s.assertElementNotPresent('css=.editable p:contains(foo Mary)')
        s.assertElementNotPresent('css=.editable p:contains(lamb. bar)')

    def test_quotation_marks_are_normalized(self):
        s = self.selenium
        self.create(u'<p>“up” and „down‟')
        self.convert()
        s.assertText('css=.editable p', '"up" and "down"')
