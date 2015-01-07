# coding: utf-8
from zeit.cms.checkout.helper import checked_out
from zeit.cms.checkout.interfaces import IWorkingcopy
from zeit.content.article.edit.browser.tests.test_edit import click
from zeit.content.article.edit.interfaces import IEditableBody
from zeit.edit.interfaces import IElementFactory
import transaction
import unittest
import zeit.content.article.testing
import zope.component


class FindDOMTest(zeit.content.article.testing.SeleniumTestCase):

    def setUp(self):
        super(FindDOMTest, self).setUp()
        self.open('/@@/zeit.content.article.edit.browser.tests.fixtures'
                  '/replace.html')

    def test_no_current_selection_starts_search_at_beginning_of_node(self):
        self.eval(
            'zeit.content.article.find_next('
            'document.getElementById("one"), "foo")')
        self.assertEqual(
            0, self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            3, self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_starts_search_at_current_selection_if_one_exists(self):
        self.eval('zeit.content.article.select('
                  'document.getElementById("two").firstChild, 4, 4)')
        self.eval(
            'zeit.content.article.find_next('
            'document.getElementById("two"), "foo")')
        self.assertEqual(
            8, self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            11, self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_searching_backward(self):
        self.eval('zeit.content.article.select('
                  'document.getElementById("two").firstChild, 4, 4)')
        self.eval(
            'zeit.content.article.find_next('
            'document.getElementById("two"), "foo", '
            'zeit.content.article.BACKWARD)')
        self.assertEqual(
            0, self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            3, self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_setting_case_insensitive_ignores_case(self):
        self.eval(
            'zeit.content.article.find_next('
            'document.getElementById("one"), "FoO")')
        self.assertEqual(
            0, self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            3, self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_selection_outside_of_node_is_ignored(self):
        self.eval('zeit.content.article.select('
                  'document.getElementById("one").firstChild, 4, 4)')
        self.eval(
            'zeit.content.article.find_next('
            'document.getElementById("two"), "foo")')
        self.assertEqual(
            0, self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            3, self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_not_found_moves_to_sibling_text(self):
        self.eval('zeit.content.article.select('
                  'window.jQuery("#three b")[0].firstChild, 0, 0)')
        self.eval(
            'zeit.content.article.find_next('
            'document.getElementById("content"), "foo")')
        self.assertEqual(
            1, self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            4, self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_not_found_moves_to_sibling_element(self):
        self.eval('zeit.content.article.select('
                  'document.getElementById("one").firstChild, 4, 4)')
        self.eval(
            'zeit.content.article.find_next('
            'document.getElementById("content"), "foo")')
        self.assertEqual(
            'two', self.eval(
                'window.getSelection().getRangeAt(0).startContainer'
                '.parentNode.id'))
        self.assertEqual(
            0, self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            3, self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_moving_to_sibling_starts_from_the_beginning(self):
        self.eval('zeit.content.article.select('
                  'document.getElementById("three").firstChild, 0, 3)')
        self.eval(
            'zeit.content.article.find_next('
            'document.getElementById("content"), "foo")')
        self.assertEqual(
            1, self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            4, self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_not_found_moves_to_parent_sibling(self):
        self.eval('zeit.content.article.select('
                  'document.getElementById("list-c").firstChild, 3, 3)')
        self.eval(
            'zeit.content.article.find_next('
            'document.getElementById("content"), "foo")')
        self.assertEqual(
            'three', self.eval(
                'window.getSelection().getRangeAt(0).startContainer'
                '.parentNode.id'))
        self.assertEqual(
            0, self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            3, self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_not_found_at_all_returns_special_value(self):
        self.eval('zeit.content.article.select('
                  'document.getElementById("three").firstChild, 0, 0)')
        self.assertEqual(
            -1, self.eval(
                'zeit.content.article.find_next('
                'document.getElementById("content"), "nonexistent")'
                '["position"]'))


class FindReplaceTest(
    zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_finding_text_works_accross_non_text_blocks(self):
        s = self.selenium
        self.add_article()
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                co = list(IWorkingcopy(None).values())[0]
                body = IEditableBody(co)
                p_factory = zope.component.getAdapter(
                    body, IElementFactory, 'p')
                img_factory = zope.component.getAdapter(
                    body, IElementFactory, 'image')
                paragraph = p_factory()
                paragraph.text = 'foo bar baz'
                img_factory()
                paragraph = p_factory()
                paragraph.text = 'foo baz'
                transaction.commit()
        s.refresh()
        para = 'css=.block.type-p .editable p'
        s.waitForElementPresent(para)
        s.click(para)
        s.waitForElementPresent('xpath=//a[@href="show_find_dialog"]')
        click(s, 'xpath=//a[@href="show_find_dialog"]')
        s.waitForElementPresent('id=find-dialog-searchtext')
        s.type('id=find-dialog-searchtext', 'baz')
        s.click('jquery=button:contains(Weiter)')
        self.wait_for_condition(
            'window.getSelection().getRangeAt(0).startOffset == 8')
        s.click('jquery=button:contains(Weiter)')
        self.wait_for_condition(
            'window.getSelection().getRangeAt(0).startOffset == 4')

    def test_finding_text_backwards(self):
        s = self.selenium
        self.add_article()
        self.create("<p>foo bar foo</p>")
        click(s, 'xpath=//a[@href="show_find_dialog"]')
        s.waitForElementPresent('id=find-dialog-searchtext')
        s.type('id=find-dialog-searchtext', 'foo')
        s.click('jquery=button:contains(Weiter)')
        s.click('jquery=button:contains(Weiter)')
        self.wait_for_condition(
            'window.getSelection().getRangeAt(0).startOffset == 8')
        s.click(u'jquery=button:contains(Zurück)')
        self.wait_for_condition(
            'window.getSelection().getRangeAt(0).startOffset == 0')

    def test_finding_text_case_insensitive(self):
        s = self.selenium
        self.add_article()
        self.create("<p>FOO bar foo</p>")
        click(s, 'xpath=//a[@href="show_find_dialog"]')
        s.waitForElementPresent('id=find-dialog-searchtext')
        s.type('id=find-dialog-searchtext', 'fOo')
        s.click('jquery=button:contains(Weiter)')
        self.wait_for_condition(
            'window.getSelection().getRangeAt(0).startOffset == 0')

    def test_finding_text_case_sensitive(self):
        s = self.selenium
        self.add_article()
        self.create("<p>FOO bar foo</p>")
        click(s, 'xpath=//a[@href="show_find_dialog"]')
        s.waitForElementPresent('id=find-dialog-searchtext')
        s.type('id=find-dialog-searchtext', 'FOO')
        s.click('id=find-dialog-case')
        s.click('jquery=button:contains(Weiter)')
        self.wait_for_condition(
            'window.getSelection().getRangeAt(0).startOffset == 0')

    def test_replacing_single_match(self):
        s = self.selenium
        self.add_article()
        self.create("<p>foo bar baz</p>")
        click(s, 'xpath=//a[@href="show_find_dialog"]')
        s.waitForElementPresent('id=find-dialog-searchtext')
        s.type('id=find-dialog-searchtext', 'foo')
        s.type('id=find-dialog-replacement', 'qux')
        s.click('jquery=button:contains(Weiter)')
        s.click('jquery=button:contains(Ersetzen)')
        self.assertEqual('qux bar baz', s.getText('css=.block.type-p p'))

    def test_replacing_all(self):
        s = self.selenium
        self.add_article()
        self.create("<p>foo bar baz</p>")
        click(s, 'xpath=//a[@href="show_find_dialog"]')
        s.waitForElementPresent('id=find-dialog-searchtext')
        s.type('id=find-dialog-searchtext', 'foo')
        s.type('id=find-dialog-replacement', 'qux')
        s.click('jquery=button:contains(Alles ersetzen)')
        s.waitForAlert('1 Stelle(n) ersetzt.')
        s.waitForText('css=.block.type-p p', 'qux bar baz')

    def test_asks_for_confirmation_to_wrap_around_at_end(self):
        s = self.selenium
        self.add_article()
        self.create("<p>foo bar foo</p>")
        self.eval("zeit.content.article.select("
                  "window.jQuery('.block.type-p .editable p')[0].firstChild, "
                  "4, 4)")
        click(s, 'xpath=//a[@href="show_find_dialog"]')
        s.waitForElementPresent('id=find-dialog-searchtext')
        s.type('id=find-dialog-searchtext', 'foo')
        s.click('jquery=button:contains(Weiter)')
        s.click('jquery=button:contains(Weiter)')
        s.waitForConfirmation(
            'Das Textende wurde erreicht. Suche am Textanfang fortsetzen?')
        self.wait_for_condition(
            'window.getSelection().getRangeAt(0).startOffset == 0')

    def test_asks_for_confirmation_to_wrap_around_at_beginning(self):
        s = self.selenium
        self.add_article()
        self.create("<p>foo bar foo</p>")
        self.eval("zeit.content.article.select("
                  "window.jQuery('.block.type-p .editable p')[0].firstChild, "
                  "4, 4)")
        click(s, 'xpath=//a[@href="show_find_dialog"]')
        s.waitForElementPresent('id=find-dialog-searchtext')
        s.type('id=find-dialog-searchtext', 'foo')
        s.click(u'jquery=button:contains(Zurück)')
        s.click(u'jquery=button:contains(Zurück)')
        s.waitForConfirmation(
            'Der Textanfang wurde erreicht. Suche am Textende fortsetzen?')
        self.wait_for_condition(
            'window.getSelection().getRangeAt(0).startOffset == 8')

    @unittest.skip('Browser focuses funky things after one clicks cancel,'
                   'not just selenium but in real life, too.')
    def test_closes_replace_dialog_on_cancelled_wrapping_confirmation(self):
        s = self.selenium
        self.add_article()
        self.create("<p>foo bar foo</p>")
        self.eval("zeit.content.article.select("
                  "window.jQuery('.block.type-p .editable p')[0].firstChild, "
                  "4, 4)")
        click(s, 'xpath=//a[@href="show_find_dialog"]')
        s.waitForElementPresent('id=find-dialog-searchtext')
        s.type('id=find-dialog-searchtext', 'foo')
        s.click('jquery=button:contains(Weiter)')
        s.click('jquery=button:contains(Weiter)')
        confirmation = s.selenium.switch_to_alert()
        self.assertEqual(
            'Das Textende wurde erreicht. Suche am Textanfang fortsetzen?',
            confirmation.text)
        confirmation.dismiss()
        s.waitForNotVisible('id=find-dialog-searchtext')
        self.wait_for_condition(
            'window.getSelection().getRangeAt(0).startOffset == 8')

    @unittest.skip('Wrap-around breaks if there is only one editable.')
    def test_stops_wrapping_if_nothing_found_since_last_wrap(self):
        s = self.selenium
        self.add_article()
        self.create("<p>foo bar foo</p>")
        self.eval("zeit.content.article.select("
                  "window.jQuery('.block.type-p .editable p')[0].firstChild, "
                  "4, 4)")
        click(s, 'xpath=//a[@href="show_find_dialog"]')
        s.waitForElementPresent('id=find-dialog-searchtext')
        s.type('id=find-dialog-searchtext', 'baz')
        s.click('jquery=button:contains(Weiter)')
        s.waitForConfirmation(
            'Das Textende wurde erreicht. Suche am Textanfang fortsetzen?')
        s.waitForAlert('Keine weiteren Ergebnisse.')

    @unittest.skip('Need to commit this even though test is not finished.')
    def test_saves_if_replacing_ends_in_subsequent_editable(self):
        from zeit.content.article.article import Article
        from zeit.content.article.interfaces import IArticle
        with zeit.cms.testing.site(self.getRootFolder()):
            wl = zope.component.getUtility(
                zeit.cms.tagging.interfaces.IWhitelist)
            with zeit.cms.testing.interaction():
                self.repository['article'] = Article()
                with checked_out(self.repository['article']) as co:
                    zeit.cms.browser.form.apply_default_values(
                        co, IArticle)
                    co.year = 2010
                    co.ressort = u'International'
                    co.title = 'foo'
                    co.keywords = (
                        wl['testtag'], wl['testtag2'], wl['testtag3'],)
                    body = IEditableBody(co)
                    p_factory = zope.component.getAdapter(
                        body, IElementFactory, 'p')
                    img_factory = zope.component.getAdapter(
                        body, IElementFactory, 'image')
                    paragraph = p_factory()
                    paragraph.text = 'foobar'
                    img_factory()
                    paragraph = p_factory()
                    paragraph.text = 'foobaz'
        self.open('/repository/article/@@checkout')

        s = self.selenium
        s.waitForElementPresent('css=.block.type-p .editable p')
        s.click('css=.block.type-p .editable p')
        self.eval("zeit.content.article.select("
                  "window.jQuery('.block.type-p .editable p')[0].firstChild, "
                  "0, 0)")
        click(s, 'xpath=//a[@href="show_find_dialog"]')
        s.waitForElementPresent('id=find-dialog-searchtext')
        s.type('id=find-dialog-searchtext', 'foo')
        s.type('id=find-dialog-replacement', 'qux')
        s.click('jquery=button:contains(Weiter)')
        s.click('jquery=button:contains(Ersetzen)')
        s.click('jquery=button:contains(Weiter)')
        s.click('jquery=button:contains(Ersetzen)')
        s.click('css=.find-dialog button.ui-dialog-titlebar-close')
        s.click('css=.wired')
        s.waitForTextPresent('quxbar')
        s.waitForTextPresent('quxbaz')
