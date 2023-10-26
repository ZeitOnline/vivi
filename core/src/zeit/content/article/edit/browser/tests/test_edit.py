# coding: utf8
from selenium.webdriver.common.keys import Keys
from unittest import mock
from zeit.content.article.edit.browser.edit import SaveText, AutoSaveText
import gocept.testing.mock
import json
import lxml.objectify
import time
import transaction
import unittest
import zeit.cms.content.field
import zeit.content.article.article
import zeit.content.article.edit.body
import zeit.content.article.edit.browser.testing
import zeit.content.article.testing
import zope.component


def click(selenium, locator):
    # XXX The normal click() causes the editable to lose focus. Why?
    selenium.mouseDown(locator)
    selenium.mouseUp(locator)


class TextViewHelper:

    view_class = NotImplemented

    def setUp(self):
        super().setUp()
        self.patches = gocept.testing.mock.Patches()
        fake_uuid = mock.Mock()
        fake_uuid.side_effect = lambda: 'id-%s' % fake_uuid.call_count
        self.patches.add(
            'zeit.edit.container.Base._generate_block_id', fake_uuid)

    def tearDown(self):
        self.patches.reset()
        super().tearDown()

    def get_view(self, body=None):
        if body is None:
            body = ("<division><p>Para 1</p><p>Para 2</p></division>"
                    "<division><p>Para 3</p><p>Para 4</p></division>")
        article = zeit.content.article.article.Article()
        article.xml.body = lxml.objectify.XML(
            '<body>%s</body>' % body)
        for division in article.xml.body.findall('division'):
            division.set('type', 'page')
        body = zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)
        body.keys()  # force uuid generation
        view = self.view_class()
        view.context = body
        view.request = mock.Mock()
        view.request.form = {}
        view.url = mock.Mock()
        return view


class SaveTextTest(TextViewHelper,
                   zeit.content.article.testing.FunctionalTestCase):

    view_class = SaveText

    def test_update_should_remove_given_paragrahs(self):
        view = self.get_view()
        self.assertEqual(
            ['id-2', 'id-3', 'id-4', 'id-5', 'id-6'], view.context.keys())
        view.request.form['paragraphs'] = ['id-5', 'id-6']
        view.request.form['text'] = []
        view.update()
        self.assertEqual(['id-2', 'id-3', 'id-4'], view.context.keys())

    def test_update_should_add_new_paragraphs_where_old_where_removed(self):
        view = self.get_view()
        view.request.form['paragraphs'] = ['id-2', 'id-3']
        view.request.form['text'] = [
            {'factory': 'p', 'text': 'Hinter'},
            {'factory': 'p', 'text': 'den'},
            {'factory': 'p', 'text': 'Wortbergen'}]
        view.update()
        self.assertEqual(['id-7', 'id-8', 'id-9', 'id-4', 'id-5', 'id-6'],
                         view.context.keys())

    def test_update_should_append_when_no_paragraphs_are_replaced(self):
        view = self.get_view()
        view.request.form['paragraphs'] = []
        view.request.form['text'] = [
            {'factory': 'p', 'text': 'Hinter'},
            {'factory': 'p', 'text': 'den'},
            {'factory': 'p', 'text': 'Wortbergen'}]
        view.update()
        self.assertEqual(
            ['id-2', 'id-3', 'id-4', 'id-5', 'id-6', 'id-7', 'id-8', 'id-9'],
            view.context.keys())

    def test_update_should_remove_empty_paragraphs(self):
        view = self.get_view()
        view.request.form['paragraphs'] = []
        view.request.form['text'] = [
            {'factory': 'p', 'text': 'Hinter'},
            {'factory': 'p', 'text': 'den'},
            {'factory': 'p', 'text': 'Wortbergen'}]
        view.update()
        self.assertEqual(
            ['id-2', 'id-3', 'id-4', 'id-5', 'id-6', 'id-7', 'id-8', 'id-9'],
            view.context.keys())

    def test_update_should_not_trigger_reload_of_body(self):
        view = self.get_view()
        view.request.form['paragraphs'] = []
        view.request.form['text'] = []
        view.update()
        self.assertEqual([], view.signals)

    def test_unknown_factories_are_mapped_to_p(self):
        view = self.get_view()
        view.request.form['paragraphs'] = ['id-2', 'id-3']
        view.request.form['text'] = [{'factory': 'iaminvalid', 'text': 'Hinter'}]
        view.update()
        self.assertEqual('p', view.context['id-7'].type)

    def test_wild_html_should_be_munged_into_paragraph(self):
        view = self.get_view()
        view.request.form['paragraphs'] = ['id-2', 'id-3']
        view.request.form['text'] = [{'text': '\n<h3 class="supertitle"><a href="http://www.zeit.de/gesellschaft/zeitgeschehen/2010-12/asasange-festnahme-grossbritannien" title="Vergewaltigungsverdacht - Britische Polizei verhaftet Julian Assange">Vergewaltigungsverdacht</a></h3>\n<h4 class="title"><a href="http://www.zeit.de/gesellschaft/zeitgeschehen/2010-12/asasange-festnahme-grossbritannien" title="Vergewaltigungsverdacht - Britische Polizei verhaftet Julian Assange" rel="bookmark">Britische Polizei verhaftet Julian Assange</a></h4>\n<p>Julian Assange wollte sich "freiwillig" mit der britischen Polizei \ntreffen, doch jetzt klickten die Handschellen. Der untergetauchte \nWikileaks-Gr\xfcnder wurde verhaftet.&nbsp;\n\t    <a href="http://www.zeit.de/gesellschaft/zeitgeschehen/2010-12/asasange-festnahme-grossbritannien" class="more-link" rel="no-follow" title="Vergewaltigungsverdacht - Britische Polizei verhaftet Julian Assange">[weiter\u2026]</a></p>\n',  # noqa
                                      'factory': 'div'},
                                     {'text': '\n<a><strong></strong></a>',
                                      'factory': 'p'}]
        view.update()
        self.assertEqual('p', view.context['id-7'].type)


class AutoSaveTextTest(TextViewHelper,
                       zeit.content.article.testing.FunctionalTestCase):

    view_class = AutoSaveText

    def test_autosave_returns_list_of_new_paragraph_ids(self):
        view = self.get_view('')
        view.request.form['paragraphs'] = []
        view.request.form['text'] = [
            {'factory': 'p', 'text': 'Hinter'},
            {'factory': 'p', 'text': 'den'},
            {'factory': 'p', 'text': 'Wortbergen'}]
        view.update()
        result = json.loads(view.render())
        self.assertEqual(['id-2', 'id-3', 'id-4'], result['data']['new_ids'])


class TestTextEditing(
        zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super().setUp()
        self.add_article()

    def test_paragraph_etc_should_not_appear_as_modules(self):
        s = self.selenium
        s.assertElementNotPresent('css=.block.type-p')
        s.waitForNotVisible('css=.message')
        s.click('link=Struktur')
        s.waitForElementPresent(
            'jquery=#article-modules .module:contains(Video)')
        s.assertElementNotPresent(
            '//*[@id="article-modules"]//*'
            '[contains(@class, "module") and contains(., "<p>")]')

    def test_clicking_empty_paragraph_at_end_should_create_paragraph(self):
        s = self.selenium
        s.assertElementNotPresent('css=.block.type-p')
        s.waitForElementPresent('css=.create-paragraph')
        s.click('css=.create-paragraph')
        s.waitForElementPresent('css=.block.type-p')

    @unittest.skip(
        'Selenium is not fast enough to click twice before the editor reloads')
    def test_clicking_empty_paragraph_twice_is_not_possible(self):
        s = self.selenium
        s.assertElementNotPresent('css=.block.type-p')
        s.waitForElementPresent('css=.create-paragraph')
        s.click('css=.create-paragraph')
        try:
            s.click('css=.create-paragraph')
        except Exception as e:
            self.assertIn('Unable to locate element', str(e))
        else:
            self.fail('second click should have raised')

    @unittest.skip('type() into content-editable does not work')
    def test_typed_text_should_be_saved(self):
        s = self.selenium
        self.create()
        s.type('css=.block.type-p .editable p', 'Saskia had a little pig.')
        self.save()
        s.waitForElementPresent('jquery=.editable p:contains(Saskia had)')

    @unittest.skip('Triggering keyup does not work')
    def test_class_attributes_should_be_removed_on_keyup(self):
        s = self.selenium
        self.create("<h4 class='title'>blubbel</h4>")
        s.assertElementPresent('css=.block.type-p h4.title')
        self.execute(
            'window.jQuery(".block.type-p .editable").trigger("keyup")')
        s.assertElementNotPresent('css=.block.type-p h4.title')

    @unittest.skip('Triggering keyup does not work')
    def test_style_attributes_should_be_removed_on_keyup(self):
        s = self.selenium
        self.create("<h4 style='display: inline'>blubbel</h4>")
        s.assertElementPresent('jquery=.block.type-p h4[style]')
        self.execute(
            'window.jQuery(".block.type-p .editable").trigger("keyup")')
        s.assertElementNotPresent('jquery=.block.type-p h4[style]')

    def test_consequent_paragraphs_should_be_editable_together(self):
        s = self.selenium
        self.create('<p>foo</p><p>bar</p>')
        self.save()
        s.waitForCssCount('css=.block.type-p', 2)
        s.click('css=.block.type-p .editable')
        s.assertCssCount('css=.block.type-p', 1)
        s.assertCssCount('css=.block.type-p .editable > *', 2)

    @unittest.skip('type() into content-editable does not work')
    def test_newline_should_create_paragraph(self):
        s = self.selenium
        self.create()
        s.type('css=.block.type-p .editable p', 'First paragraph.')
        s.click('xpath=//a[@href="formatBlock/h3"]')
        s.keyPress('css=.block.type-p .editable h3', Keys.RETURN)
        s.type('css=.block.type-p .editable h3', 'Second paragraph.')
        s.waitForElementPresent(
            'jquery=.editable p:contains(Second paragraph)')

    def select_text(self):
        s = self.selenium
        self.create('<p>I want to link something</p>'
                    '<p>And I need distance<p>'
                    '<p>from the bottom landing zone<p>')
        self.execute("""(function() {
            var p = window.jQuery('.block.type-p .editable p')[0];
            var range = window.getSelection().getRangeAt(0);
            range.setStart(p.firstChild, 10);
            range.setEnd(p.firstChild, 14);
        })();""")
        s.assertElementNotPresent('xpath=//a[@href="http://example.com/"]')

    def test_editing_should_end_on_content_drag(self):
        self.add_testcontent_to_clipboard()
        s = self.selenium
        self.create('<p>foo</p><p>bar</p>')
        self.save()
        s.waitForCssCount('css=.block.type-p', 2)
        # Start editing
        time.sleep(0.25)
        s.click('css=.block.type-p .editable')
        s.waitForElementPresent('css=.block.type-p.editing')
        time.sleep(0.25)
        # start dragging
        s.dragAndDrop('//li[@uniqueid="Clip/testcontent"]', '+100,+0')
        time.sleep(0.25)
        # Saved, no longer ediable
        s.waitForElementNotPresent('css=.block.type-p.editing')

    @unittest.skip('wait for gocept.selenium to implement element positions '
                   'and for webdriver to allow clicking inside a paragraph')
    def test_toolbar_moves_only_vertically(self):
        s = self.selenium
        self.create('<p>foo</p><p>bar</p>')
        self.save()
        s.waitForCssCount('css=.block.type-p', 2)
        # Start editing
        s.click('css=.block.type-p .editable')
        toolbar = 'css=.block.type-p.editing .rte-toolbar'
        s.waitForElementPresent(toolbar)
        x = s.getElementPositionLeft(toolbar)
        y = s.getElementPositionTop(toolbar)
        s.click('jquery=.block.type-p .editable p:contains(bar)')
        while s.getElementPositionTop(toolbar) - y < 10:
            time.sleep(0.1)
        self.assertEqual(x, s.getElementPositionLeft(toolbar))

    @unittest.skip('webdriver cannot click according to a character position')
    def test_click_in_paragraph_starts_editing_and_places_cursor_exactly_there(
            self):
        pass


@unittest.skip('Sending arrow keys does not work')
class TestEditingMultipleParagraphs(
        zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super().setUp()
        from zeit.cms.checkout.helper import checked_out
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
            paragraph.text = 'foo'
            co.body.create_item('image')
            paragraph = co.body.create_item('p')
            paragraph.text = 'bar'
        self.open('/repository/article/@@checkout')

    def test_arrow_up_moves_across_non_text_block_and_places_cursor_at_end(
            self):
        s = self.selenium
        second_p = (
            '//*[contains(@class, "block") and contains(@class, "type-p")][2]'
            '//*[contains(@class, "editable")]/p')
        s.waitForElementPresent(second_p)
        s.click(second_p)
        s.keyDown(second_p, Keys.ARROW_UP)
        s.keyUp(second_p, Keys.ARROW_UP)
        self.wait_for_condition(
            'window.getSelection().getRangeAt(0).startOffset == 3')

    def test_arrow_down_moves_across_non_text_block_and_places_cursor_at_start(
            self):
        s = self.selenium
        first_p = 'css=.block.type-p .editable p'
        s.waitForElementPresent(first_p)
        s.click(first_p)
        s.keyDown(first_p, Keys.ARROW_DOWN)
        s.keyUp(first_p, Keys.ARROW_DOWN)
        self.wait_for_condition(
            'window.getSelection().getRangeAt(0).startOffset == 0')


class TestLinkEditing(
        zeit.content.article.edit.browser.testing.EditorTestCase):

    window_width = 1600
    window_height = 1200

    def setUp(self):
        super().setUp()
        self.add_article()

    def select_text(self):
        s = self.selenium
        self.create('<p>I want to link something</p>'
                    '<p>And I need distance<p>'
                    '<p>from the bottom landing zone<p>')
        self.execute("""(function() {
            var p = window.jQuery('.block.type-p .editable p')[0];
            var range = window.getSelection().getRangeAt(0);
            range.setStart(p.firstChild, 10);
            range.setEnd(p.firstChild, 14);
        })();""")
        s.assertElementNotPresent('xpath=//a[@href="http://example.com/"]')

    def select_link(self, additional='', href='http://example.com/'):
        s = self.selenium
        self.create(
            '<p>I want to <a href="{1}" {0}>link</a> something</p>'.format(
                additional, href))
        self.execute("""(function() {
            var p = window.jQuery('.block.type-p .editable p')[0];
            var range = window.getSelection().getRangeAt(0);
            range.setStart(p, 1);
            range.setEnd(p, 2);
        })();""")
        s.assertElementPresent('xpath=//a[@href="{0}"]'.format(href))

    def test_links_should_be_addable(self):
        s = self.selenium
        self.select_text()
        click(s, 'xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input input[name=href]')
        s.type('css=.link_input input[name=href]', 'http://example.com/')
        s.click('css=.link_input button[name=insert_link_ok]')
        s.waitForElementPresent('xpath=//a[@href="http://example.com/"]')

    def test_pressing_enter_should_add_link(self):
        s = self.selenium
        self.select_text()
        click(s, 'xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input input[name=href]')
        s.type('css=.link_input input[name=href]', 'http://example.com/')
        s.keyDown('css=.link_input input[name=href]', Keys.ENTER)
        s.waitForElementPresent('xpath=//a[@href="http://example.com/"]')

    def test_target_should_be_editable(self):
        s = self.selenium
        self.select_text()
        click(s, 'xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input input[name=href]')
        s.select('css=.link_input select[name=target]', 'label=Neues Fenster')
        s.type('css=.link_input input[name=href]', 'http://example.com/')
        s.click('css=.link_input button[name=insert_link_ok]')
        s.waitForElementPresent(
            'xpath=//a[@href="http://example.com/" and @target="_blank"]')

    def test_edit_on_link_should_set_href_in_input(self):
        s = self.selenium
        self.select_link()
        click(s, 'xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input input[name=href]')
        s.assertValue(
            'css=.link_input input[name=href]', 'http://example.com/')

    def test_edit_on_link_should_set_target_to_select(self):
        s = self.selenium
        self.select_link(additional='target="_blank"')
        click(s, 'xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input input[name=href]')
        s.assertSelectedLabel(
            'css=.link_input select[name=target]', 'Neues Fenster')

    def test_target_colorbox_should_set_class_attribute(self):
        s = self.selenium
        self.select_link(additional='target="_blank"')
        click(s, 'xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input input[name=href]')
        s.select('css=.link_input select[name=target]', 'label=Colorbox')
        s.click('css=.link_input button[name=insert_link_ok]')
        s.waitForElementPresent(
            'xpath=//a[@href="http://example.com/" and @class="colorbox"]')

    def test_edit_link_on_colorbox_should_set_target(self):
        s = self.selenium
        self.select_link(additional='class="colorbox"')
        click(s, 'xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input input[name=href]')
        s.assertSelectedLabel(
            'css=.link_input select[name=target]', 'Colorbox')

    def test_edit_should_highlight_link_being_edited(self):
        s = self.selenium
        self.select_text()
        click(s, 'xpath=//a[@href="insert_link"]')
        s.assertElementPresent('css=.editable a.link-edit')

    def test_links_should_be_removable(self):
        s = self.selenium
        self.select_link()
        click(s, 'xpath=//a[@href="unlink"]')
        s.waitForElementNotPresent('xpath=//a[@href="http://example.com/"]')

    @unittest.skip('FF34 loses editable focus after cancel button is clicked')
    def test_cancel_should_keep_selection(self):
        s = self.selenium
        self.select_text()
        click(s, 'xpath=//a[@href="insert_link"]')
        s.waitForElementPresent('css=.editable a')
        s.click('css=.link_input button[name=insert_link_cancel]')
        result = s.getEval("""(function(s) {
            var range = window.getSelection().getRangeAt(0);
            return range.startContainer.childNodes[range.startOffset].data
        })(this);""")
        self.assertEqual('link', result)

    @unittest.skip('FF34 loses editable focus after OK button is clicked')
    def test_insert_link_should_select_link(self):
        s = self.selenium
        self.select_text()
        click(s, 'xpath=//a[@href="insert_link"]')
        s.type('css=.link_input input[name=href]', 'http://example.com/')
        s.click('css=.link_input button[name=insert_link_ok]')
        s.waitForElementPresent('xpath=//a[@href="http://example.com/"]')
        result = s.getEval("""(function(s) {
            var range = window.getSelection().getRangeAt(0);
            return range.startContainer.childNodes[range.startOffset].nodeName;
        })(this);""")
        self.assertEqual('A', result)

    @unittest.skip('FF34 loses editable focus after cancel button is clicked')
    def test_edit_link_with_cancel_should_keep_link_selected(self):
        s = self.selenium
        self.select_link()
        click(s, 'xpath=//a[@href="insert_link"]')
        s.click('css=.link_input button[name=insert_link_cancel]')
        result = s.getEval("""(function(s) {
            var range = window.getSelection().getRangeAt(0);
            return range.startContainer.childNodes[range.startOffset].nodeName;
        })(this);""")
        self.assertEqual('A', result)

    def test_cancel_should_not_insert_link(self):
        s = self.selenium
        self.select_text()
        click(s, 'xpath=//a[@href="insert_link"]')
        s.waitForElementPresent('css=.editable a')
        s.click('css=.link_input button[name=insert_link_cancel]')
        s.waitForElementNotPresent('css=.editable a')

    def test_dialog_should_accept_content_drop(self):
        self.add_testcontent_to_clipboard()
        s = self.selenium
        self.select_text()
        click(s, 'xpath=//a[@href="insert_link"]')
        # We need to scroll the inner "frame" to top, otherwise dragging will
        # get confused:
        self.execute(
            "document.getElementById('cp-content-inner').scrollTop = 0;")
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/testcontent"]', 'css=.link_input')
        s.assertValue('css=.link_input input[name=href]',
                      'http://www.zeit.de/testcontent')

    def test_drag_while_dialog_open_should_not_end_edit(self):
        self.add_testcontent_to_clipboard()
        s = self.selenium
        self.select_text()
        click(s, 'xpath=//a[@href="insert_link"]')
        s.dragAndDrop('//li[@uniqueid="Clip/testcontent"]', '+100,+0')
        time.sleep(0.25)
        # Element still there
        s.assertElementPresent('css=.block.type-p.editing')

    def test_selecting_mail_hides_web_inputs_and_shows_mail_inputs(self):
        self.add_testcontent_to_clipboard()
        s = self.selenium
        self.select_text()
        click(s, 'xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input select[name=service]')
        s.select('css=.link_input select[name=service]', 'label=E-Mail')
        s.waitForVisible('css=.link_input input[name=mailto]')
        s.waitForVisible('css=.link_input input[name=subject]')
        s.assertNotVisible('css=.link_input input[name=href]')
        s.assertNotVisible('css=.link_input select[name=target]')

    def test_selecting_web_hides_mail_inputs_and_shows_web_inputs(self):
        self.add_testcontent_to_clipboard()
        s = self.selenium
        self.select_text()
        click(s, 'xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input select[name=service]')
        s.select('css=.link_input select[name=service]', 'label=E-Mail')
        s.select('css=.link_input select[name=service]', 'label=Web')
        s.waitForVisible('css=.link_input input[name=href]')
        s.waitForVisible('css=.link_input select[name=target]')
        s.assertNotVisible('css=.link_input input[name=mailto]')
        s.assertNotVisible('css=.link_input input[name=subject]')

    def test_selecting_mail_link_opens_linkbar_in_mail_mode(self):
        self.add_testcontent_to_clipboard()
        s = self.selenium
        self.select_link(href='mailto:foo@example.com')
        click(s, 'xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input select[name=service]')
        s.assertSelectedLabel(
            'css=.link_input select[name=service]', 'E-Mail')
        s.assertValue('css=.link_input input[name=mailto]', 'foo@example.com')
        s.assertValue('css=.link_input input[name=subject]', '')

    def test_selecting_mail_link_with_subject_opens_linkbar_in_mail_mode(self):
        self.add_testcontent_to_clipboard()
        s = self.selenium
        self.select_link(href='mailto:foo@example.com?subject=b%C3%A4r')
        click(s, 'xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input select[name=service]')
        s.assertSelectedLabel(
            'css=.link_input select[name=service]', 'E-Mail')
        s.assertValue('css=.link_input input[name=mailto]', 'foo@example.com')
        s.assertValue('css=.link_input input[name=subject]', 'bär')

    def test_pressing_enter_in_mail_mode_adds_mailto_link(self):
        s = self.selenium
        self.select_text()
        click(s, 'xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input input[name=href]')
        s.select('css=.link_input select[name=service]', 'label=E-Mail')
        s.waitForVisible('css=.link_input input[name=mailto]')
        s.type('css=.link_input input[name=mailto]', 'foo@example.com')
        s.keyDown('css=.link_input input[name=mailto]', Keys.ENTER)
        s.waitForElementPresent('xpath=//a[@href="mailto:foo@example.com"]')

    def test_pressing_enter_in_mail_mode_with_subject_adds_mailto_link(self):
        s = self.selenium
        self.select_text()
        click(s, 'xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input input[name=href]')
        s.select('css=.link_input select[name=service]', 'label=E-Mail')
        s.waitForVisible('css=.link_input input[name=mailto]')
        s.type('css=.link_input input[name=mailto]', 'foo@example.com')
        s.type('css=.link_input input[name=subject]', 'bär')
        s.keyDown('css=.link_input input[name=mailto]', Keys.ENTER)
        s.waitForElementPresent(
            'xpath=//a[@href="mailto:foo@example.com?subject=b%C3%A4r"]')

    def test_checking_nofollow_sets_rel_attribute(self):
        s = self.selenium
        self.select_link()
        click(s, 'xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input input[name=href]')
        s.click('css=.link_input input[name=nofollow]')
        s.click('css=.link_input button[name=insert_link_ok]')
        s.waitForElementPresent(
            'xpath=//a[@href="http://example.com/" and @rel="nofollow"]')

    def test_rel_nofollow_checks_checkbox(self):
        s = self.selenium
        self.select_link(additional='rel="nofollow"')
        click(s, 'xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input input[name=href]')
        s.assertChecked('css=.link_input input[name=nofollow]')

    def test_unchecking_nofollow_removes_rel_attribute(self):
        s = self.selenium
        self.select_link(additional='rel="nofollow"')
        click(s, 'xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input input[name=href]')
        s.click('css=.link_input input[name=nofollow]')
        s.click('css=.link_input button[name=insert_link_ok]')
        s.waitForElementPresent(
            'xpath=//a[@href="http://example.com/" and not(@rel)]')

    def test_selecting_across_tags_inserts_multiple_link_tags(self):
        s = self.selenium
        self.create('<p>I want to link <b>some bold text</b></p>'
                    '<p>And I need distance<p>'
                    '<p>from the bottom landing zone<p>')
        self.execute("""(function() {
            var p = window.jQuery('.block.type-p .editable p')[0];
            var range = window.getSelection().getRangeAt(0);
            range.setStart(p.firstChild, 10);
            var b = window.jQuery('.block.type-p .editable b')[0];
            range.setEnd(b.firstChild, 9);
        })();""")
        click(s, 'xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input input[name=href]')
        s.type('css=.link_input input[name=href]', 'http://example.com/')
        s.click('css=.link_input button[name=insert_link_ok]')
        s.waitForXpathCount('//a[@href="http://example.com/"]', 2)


class TestFolding(
        zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super().setUp()
        self.add_article()

    def assert_foldable(self, block):
        s = self.selenium
        self.create_block(block)
        s.assertElementNotPresent(f'css=.block.type-{block}.folded')
        s.click(f'css=.block.type-{block} .edit-bar .fold-link')
        s.waitForElementPresent(f'css=.block.type-{block}.folded')
        s.click(f'css=.block.type-{block} .edit-bar .fold-link')
        s.waitForElementNotPresent(f'css=.block.type-{block}.folded')

    @unittest.skip(
        'We would need to bypass the first hidden image block (main image), '
        'but writing that down is not worth the hassle')
    def test_image_should_be_foldable(self):
        self.assert_foldable('image')

    def test_gallery_should_be_foldable(self):
        self.assert_foldable('gallery')

    def test_citation_should_be_foldable(self):
        self.assert_foldable('citation')

    def test_citation_comment_should_be_foldable(self):
        self.assert_foldable('citation_comment')

    def test_infobox_should_be_foldable(self):
        self.assert_foldable('infobox')

    def test_portraitbox_should_be_foldable(self):
        self.assert_foldable('portraitbox')

    def test_raw_should_be_foldable(self):
        self.assert_foldable('raw')

    def test_video_should_be_foldable(self):
        self.assert_foldable('video')

    def test_liveblog_should_be_foldable(self):
        self.assert_foldable('liveblog')

    def test_folding_state_is_preserved_between_editing_text(self):
        self.create_block('video')
        s = self.selenium
        s.click('css=.block.type-video .edit-bar .fold-link')
        s.waitForElementPresent('css=.block.type-video.folded')
        s.click('css=.create-paragraph')
        s.waitForCssCount('css=.block.type-p', 1)
        self.save()
        s.waitForElementPresent('css=.block.type-video.folded')


class TestDivision(
        zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super().setUp()
        self.add_article()

    def create_division(self):
        s = self.selenium
        s.assertElementNotPresent('css=.block.type-division')
        s.waitForElementPresent('link=Struktur')
        s.waitForNotVisible('css=.message')
        s.click('link=Struktur')
        s.waitForElementPresent(
            'css=#article-modules .module[cms\\:block_type=division]')
        s.dragAndDropToObject(
            'css=#article-modules .module[cms\\:block_type=division]',
            'css=#editable-body > .landing-zone', '10,10')
        s.waitForElementPresent('css=.block.type-division')

    def test_division_should_have_editable_teaser(self):
        self.create_division()
        s = self.selenium
        s.waitForElementPresent('css=.type-division textarea')
        s.type('css=.type-division textarea', 'Division teaser')
        s.keyPress('css=.type-division textarea', Keys.TAB)
        s.waitForElementNotPresent('css=.field.dirty')
        # Re-open the page and verify that the data is still there
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent('css=.type-division textarea')
        s.assertValue('css=.type-division textarea', 'Division teaser')


class TestLimitedInput(
        zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super().setUp()
        self.add_article()

    @unittest.skip("no typeKeys 'til webdriver")
    def test_limitation_should_decrease_on_input(self):
        s = self.selenium
        s.waitForElementPresent('xpath=//span[@class="charlimit"]')
        s.assertText('xpath=//span[@class="charlimit"]', '170 Zeichen')
        s.focus('id=teaser-text.teaserText')
        s.typeKeys('id=teaser-text.teaserText', 'Saskia had a little pig')
        # Due to a bug in selenium, we have to release the key manually.
        # That is selenium currently has registered everything but the trailing
        # "g" character. Nevertheless we should check whether our input has
        # decreased the charlimit at all.
        s.assertText('xpath=//span[@class="charlimit"]', '148 Zeichen')
        s.keyUp('id=teaser-text.teaserText', 'g')
        # Now selenium has recieved the whole input.
        s.assertText('xpath=//span[@class="charlimit"]', '147 Zeichen')


class TestCountedInput(
        zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super().setUp()
        self.add_article()

    @unittest.skip("no typeKeys 'til webdriver")
    def test_input_should_be_counted_on_input(self):
        s = self.selenium
        s.waitForElementPresent('xpath=//span[@class="charlimit"]')
        s.assertText('xpath=//span[@class="charcount"]', '0 Zeichen')
        self.create()
        s.typeKeys('css=.block.type-p .editable p', 'Saskia had a little pig')
        self.save()
        s.assertText('xpath=//span[@class="charcount"]', '23 Zeichen')

    @unittest.skip("no typeKeys 'til webdriver")
    def test_deleting_paragraphs_should_update_counter(self):
        s = self.selenium
        s.waitForElementPresent('xpath=//span[@class="charlimit"]')
        self.create()
        s.typeKeys('css=.block.type-p .editable p', 'Saskia had a little pig')
        self.save()
        s.assertText('xpath=//span[@class="charcount"]', '23 Zeichen')
        s.mouseOver('css=.block')
        s.click('css=.block a.delete-link')
        s.waitForElementNotPresent('css=.block.type-p .editable p')
        s.assertText('xpath=//span[@class="charcount"]', '0 Zeichen')


class AutoSaveIntegration(
        zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super().setUp()
        self.add_article()
        self.wait_for_dotted_name("zeit.content.article.Editable")
        self.execute(
            "zeit.content.article.Editable.prototype.autosave_interval = 0.2;")

    def assert_paragraphs(self, *contents):
        transaction.abort()
        wc = self.getRootFolder()['workingcopy']['zope.user']
        article = next(wc.values())
        self.assertEqual(
            contents, tuple(el.text for el in article.xml.xpath('//p')))

    def test_text_is_saved_correctly_by_autosave_and_normal_save_after(self):
        self.create('<p>foo</p><p>bar</p>')
        self.wait_for_condition(
            "window.jQuery('.block.type-p .editable')[0]"
            ".editable.edited_paragraphs.length == 2")
        self.assert_paragraphs('foo', 'bar')
        self.save()
        self.assert_paragraphs('foo', 'bar')


class DirtySaveVersusPersistTests(
        zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super().setUp()
        self.add_article()
        self.wait_for_dotted_name("zeit.content.article.Editable")
        self.execute(
            "zeit.content.article.Editable.prototype.persist = function () { "
            "  zeit.edit.persist_called = true; }")

    def save(self):
        # Override self.save() as the superclass expects that save is working
        # properly but as we mocked persist it doesn't.
        self.execute('%s.save()' % self.get_js_editable())

    def test_does_not_save_on_server_if_not_dirty(self):
        self.create('<p>foo</p><p>bar</p>')
        self.mark_dirty(status=False)
        self.save()
        self.assertEqual(None, self.eval("zeit.edit.persist_called"))

    def test_save_on_server_if_dirty(self):
        self.create('<p>foo</p><p>bar</p>')
        self.mark_dirty(status=True)
        self.save()
        self.assertEqual(True, self.eval("zeit.edit.persist_called"))

    def test_toolbar_actions_mark_editor_as_dirty(self):
        self.create('<p>foo</p><p>bar</p>')
        self.mark_dirty(status=False)
        click(self.selenium, 'link=H3')
        self.assertEqual(True, self.eval(self.get_js_editable() + ".dirty"))

    def test_dirty_flag_persists_on_movement_keypress(self):
        self.create('<p>foo</p><p>bar</p>')
        self.mark_dirty(status=True)
        self.selenium.keyPress(
            'css=.block.type-p .editable p', Keys.ARROW_LEFT)
        self.save()
        self.assertEqual(True, self.eval("zeit.edit.persist_called"))


@unittest.skip("no typeKeys 'til webdriver")
class BackButtonPreventionTest(
        zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_backspace_somewhere_does_not_cause_back_button(self):
        pass

    def test_backspace_in_textinput_and_textarea_still_works(self):
        pass

    def test_backspace_in_edit_mode_still_works(self):
        pass
