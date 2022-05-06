# coding: utf-8
from zeit.cms.checkout.helper import checked_out
from zeit.cms.checkout.interfaces import IWorkingcopy
from zeit.content.article.edit.browser.tests.test_edit import click
import transaction
import unittest
import zeit.cms.content.field
import zeit.content.article.testing
import zope.component


class FindDOMTest(zeit.content.article.testing.SeleniumTestCase):

    def setUp(self):
        super().setUp()
        self.open('/@@/zeit.content.article.edit.browser.tests.fixtures'
                  '/replace.html')

    def test_no_current_selection_starts_search_at_beginning_of_node(self):
        self.execute(
            'zeit.content.article.find_next('
            'document.getElementById("one"), "foo")')
        self.assertEqual(
            0, self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            3, self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_starts_search_at_current_selection_if_one_exists(self):
        self.execute('zeit.content.article.select('
                     'document.getElementById("two").firstChild, 4, 4)')
        self.execute(
            'zeit.content.article.find_next('
            'document.getElementById("two"), "foo")')
        self.assertEqual(
            8, self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            11, self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_searching_backward(self):
        self.execute('zeit.content.article.select('
                     'document.getElementById("two").firstChild, 4, 4)')
        self.execute(
            'zeit.content.article.find_next('
            'document.getElementById("two"), "foo", '
            'zeit.content.article.BACKWARD)')
        self.assertEqual(
            0, self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            3, self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_setting_case_insensitive_ignores_case(self):
        self.execute(
            'zeit.content.article.find_next('
            'document.getElementById("one"), "FoO")')
        self.assertEqual(
            0, self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            3, self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_selection_outside_of_node_is_ignored(self):
        self.execute('zeit.content.article.select('
                     'document.getElementById("one").firstChild, 4, 4)')
        self.execute(
            'zeit.content.article.find_next('
            'document.getElementById("two"), "foo")')
        self.assertEqual(
            0, self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            3, self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_not_found_moves_to_sibling_text(self):
        self.execute('zeit.content.article.select('
                     'window.jQuery("#three b")[0].firstChild, 0, 0)')
        self.execute(
            'zeit.content.article.find_next('
            'document.getElementById("content"), "foo")')
        self.assertEqual(
            1, self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            4, self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_not_found_moves_to_sibling_element(self):
        self.execute('zeit.content.article.select('
                     'document.getElementById("one").firstChild, 4, 4)')
        self.execute(
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
        self.execute('zeit.content.article.select('
                     'document.getElementById("three").firstChild, 0, 3)')
        self.execute(
            'zeit.content.article.find_next('
            'document.getElementById("content"), "foo")')
        self.assertEqual(
            1, self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            4, self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_not_found_moves_to_parent_sibling(self):
        self.execute('zeit.content.article.select('
                     'document.getElementById("list-c").firstChild, 3, 3)')
        self.execute(
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
        self.execute('zeit.content.article.select('
                     'document.getElementById("three").firstChild, 0, 0)')
        self.assertEqual(
            -1, self.eval(
                'zeit.content.article.find_next('
                'document.getElementById("content"), "nonexistent")'
                '["position"]'))


@unittest.skip('Functionality is broken under FF72')
class FindReplaceTest(
        zeit.content.article.edit.browser.testing.EditorTestCase):

    def add_article(self):
        super().add_article()
        below_body = '#edit-form-recensions .edit-bar .fold-link'
        self.eval(
            'document.querySelector("%s").scrollIntoView()' % below_body)

    def test_finding_text_works_accross_non_text_blocks(self):
        s = self.selenium
        self.add_article()
        transaction.abort()
        co = list(IWorkingcopy(None).values())[0]
        paragraph = co.body.create_item('p')
        paragraph.text = 'foo bar baz'
        co.body.create_item('image')
        paragraph = co.body.create_item('p')
        paragraph.text = 'foo baz'
        transaction.commit()

        s.refresh()
        para = 'css=.block.type-p .editable p'
        s.waitForElementPresent(para)
        self.eval('document.querySelector("%s").scrollIntoView()' %
                  para.replace('css=', ''))
        s.clickAt(para, '5,5')
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
        s.click('jquery=button:contains(Zurück)')
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
        self.execute(
            "zeit.content.article.select("
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
        self.execute(
            "zeit.content.article.select("
            "window.jQuery('.block.type-p .editable p')[0].firstChild, "
            "4, 4)")
        click(s, 'xpath=//a[@href="show_find_dialog"]')
        s.waitForElementPresent('id=find-dialog-searchtext')
        s.type('id=find-dialog-searchtext', 'foo')
        s.click('jquery=button:contains(Zurück)')
        s.click('jquery=button:contains(Zurück)')
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
        self.execute(
            "zeit.content.article.select("
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
        self.execute(
            "zeit.content.article.select("
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
        wl = zope.component.getUtility(zeit.cms.tagging.interfaces.IWhitelist)
        self.repository['article'] = Article()
        with checked_out(self.repository['article']) as co:
            zeit.cms.content.field.apply_default_values(
                co, IArticle)
            co.year = 2010
            co.ressort = 'International'
            co.title = 'foo'
            co.keywords = (
                wl.get('Testtag'), wl.get('Testtag2'), wl.get('Testtag3'),)
            paragraph = co.body.create_item('p')
            paragraph.text = 'foobar'
            paragraph = co.body.create_item('image')
            paragraph = co.body.create_item('p')
            paragraph.text = 'foobaz'
        self.open('/repository/article/@@checkout')

        s = self.selenium
        s.waitForElementPresent('css=.block.type-p .editable p')
        s.click('css=.block.type-p .editable p')
        self.execute(
            "zeit.content.article.select("
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
