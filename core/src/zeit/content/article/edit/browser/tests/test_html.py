# coding: utf8
import zeit.content.article.edit.browser.testing


class HTMLConvertTest(
        zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super().setUp()
        self.add_article()

    def convert(self):
        self.execute(
            "window.zeit.content.article.html.to_xml("
            "window.jQuery('.editable')[0])")

    def test_h3_is_translated_to_intertitle(self):
        s = self.selenium
        self.create('<h3>foo</h3>')
        self.convert()
        s.assertElementPresent('jquery=.editable intertitle:contains(foo)')

    def test_div_is_translated_to_p(self):
        s = self.selenium
        self.create('<div>foo</div>')
        self.convert()
        s.assertElementPresent('jquery=.editable p:contains(foo)')

    def test_b_is_translated_to_strong(self):
        s = self.selenium
        self.create('<p><b>foo</b></p>')
        self.convert()
        s.assertElementPresent('jquery=.editable p strong:contains(foo)')

    def test_i_is_translated_to_em(self):
        s = self.selenium
        self.create('<p><i>foo</i></p>')
        self.convert()
        s.assertElementPresent('jquery=.editable p em:contains(foo)')

    def test_double_p_is_removed(self):
        s = self.selenium
        self.create('<p><p>foo</p>')
        self.convert()
        s.assertElementPresent('jquery=.editable p:contains(foo)')
        s.assertXpathCount('//*[@class="editable"]//p', 1)

    def test_empty_p_are_removed(self):
        s = self.selenium
        self.create('<p>foo</p><p></p><p></p>')
        self.convert()
        self.assertEqual(
            '<p>foo</p>', self.eval('window.jQuery(".editable")[0].innerHTML'))
        s.assertXpathCount('//*[@class="editable"]//p', 1)

    def test_all_double_brs_are_translated_to_p(self):
        s = self.selenium
        self.create('<p>foo<br><br>bar<br><br>baz</p>')
        self.convert()
        s.waitForCssCount('css=.editable p', 3)
        self.assertEqual('<p>foo</p><p>bar</p><p>baz</p>',
                         self.eval('window.jQuery(".editable")[0].innerHTML'))
        s.assertXpathCount('//*[@class="editable"]//br', 0)

    def test_trailing_br_does_not_break_see_BUG_1273(self):
        self.execute("""\
            window.tree = MochiKit.DOM.createDOM('p');
            window.tree.innerHTML = '<p>foo</p><br><br>';
            window.cloned = window.tree.cloneNode(true);
            window.zeit.content.article.html.to_xml(window.cloned);
        """)
        # br/br transforms to p, and empty p is removed
        self.assertEqual('<p>foo</p>', self.eval('window.cloned.innerHTML'))

    def test_single_br_is_conserved(self):
        s = self.selenium
        self.create('<p>foo<br>bar</p>')
        self.convert()
        s.assertXpathCount('//*[@class="editable"]//p', 1)
        s.assertXpathCount('//*[@class="editable"]//br', 1)

    def test_separate_single_brs_are_conserved(self):
        s = self.selenium
        self.create('<p>foo<br>bar<br>baz</p>')
        self.convert()
        s.assertXpathCount('//*[@class="editable"]//p', 1)
        s.assertXpathCount('//*[@class="editable"]//br', 2)

    def test_a_witout_href_should_be_escaped(self):
        s = self.selenium
        self.create('<p>A stupid <a>link</a>.</p>')
        self.convert()
        s.assertAttribute('css=.editable p a@href', '*#')

    def test_a_with_href_should_be_allowed(self):
        s = self.selenium
        self.create('<p>A working <a href="foo">link</a>.</p>')
        self.convert()
        s.assertAttribute('css=.editable p a@href', '*foo')

    def test_a_target_should_be_allowed(self):
        s = self.selenium
        self.create('<p>A working <a href="foo" target="_blank">link</a>.</p>')
        self.convert()
        s.assertAttribute('css=.editable p a@target', '_blank')

    def test_text_nodes_should_become_paragraphs(self):
        s = self.selenium
        self.create('Mary<p>had a little</p>')
        self.convert()
        s.assertElementPresent('jquery=.editable p:contains(Mary)')

    def test_top_level_inline_styles_are_joined_to_paragraph(self):
        s = self.selenium
        self.create('Mary <strong>had</strong> a little lamb.')
        self.convert()
        s.assertElementPresent('jquery=.editable p:contains(Mary had a)')
        s.assertElementPresent('jquery=.editable p > strong:contains(had)')

    def test_top_level_inline_styles_are_not_joined_to_existing_p(self):
        s = self.selenium
        self.create(
            '<p>foo</p>Mary <strong>had</strong> a little lamb. <p>bar</p>')
        self.convert()
        s.assertElementPresent('jquery=.editable p:contains(Mary had a)')
        s.assertElementPresent('jquery=.editable p > strong:contains(had)')
        # XXX jQuery's contains() yields incorrect results here, why?
        s.assertElementNotPresent(
            '//*[contains(@class, "editable")]//p[contains(., "foo Mary")]')
        s.assertElementNotPresent(
            '//*[contains(@class, "editable")]//p[contains(., "lamb. bar")]')

    def test_quotation_marks_are_normalized(self):
        s = self.selenium
        self.create('<p>“up” and „down‟ and «around»</p>')
        self.convert()
        s.assertText('css=.editable p', '"up" and "down" and "around"')
