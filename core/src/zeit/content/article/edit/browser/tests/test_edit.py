# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import time
import unittest2
import zeit.content.article.edit.browser.testing
import zeit.content.article.testing
import zope.component


class SaveTextTest(zeit.content.article.testing.FunctionalTestCase):

    def get_view(self, body=None):
        from zeit.content.article.edit.browser.edit import SaveText
        import lxml.objectify
        import zeit.content.article.article
        import zeit.content.article.edit.body
        if not body:
            body = ("<division><p>Para 1</p><p>Para 2</p></division>"
                     "<division><p>Para 3</p><p>Para 4</p></division>")
        article = zeit.content.article.article.Article()
        article.xml.body = lxml.objectify.XML(
            '<body>%s</body>' % body)
        for division in article.xml.body.findall('division'):
            division.set('type', 'page')
        body = zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)
        self.uuid = mock.Mock()
        self.uuid.side_effect = lambda: self.uuid.call_count
        with mock.patch('uuid.uuid4', new=self.uuid):
            body.keys()
        view = SaveText()
        view.context = body
        view.request = mock.Mock()
        view.request.form = {}
        view.url = mock.Mock()
        view.signals = []
        return view

    def test_update_should_remove_given_paragrahs(self):
        view = self.get_view()
        self.assertEqual(['2', '3', '4', '5', '6'], view.context.keys())
        view.request.form['paragraphs'] = ['5', '6']
        view.request.form['text'] = []
        view.update()
        self.assertEqual(['2', '3', '4'], view.context.keys())

    def test_update_should_add_new_paragraphs_where_old_where_removed(self):
        view = self.get_view()
        view.request.form['paragraphs'] = ['2', '3']
        view.request.form['text'] = [
            dict(factory='p', text='Hinter'),
            dict(factory='p', text='den'),
            dict(factory='p', text='Wortbergen')]
        with mock.patch('uuid.uuid4', new=self.uuid):
            view.update()
        self.assertEqual(['7', '8', '9', '4', '5', '6'],
                         view.context.keys())

    def test_update_should_append_when_no_paragraphs_are_replaced(self):
        view = self.get_view()
        view.request.form['paragraphs'] = []
        view.request.form['text'] = [
            dict(factory='p', text='Hinter'),
            dict(factory='p', text='den'),
            dict(factory='p', text='Wortbergen')]
        with mock.patch('uuid.uuid4', new=self.uuid):
            view.update()
        self.assertEqual(['2', '3', '4', '5', '6', '7', '8', '9'],
                         view.context.keys())

    def test_update_should_remove_empty_paragraphs(self):
        view = self.get_view()
        view.request.form['paragraphs'] = []
        view.request.form['text'] = [
            dict(factory='p', text='Hinter'),
            dict(factory='p', text='den'),
            dict(factory='p', text='Wortbergen')]
        with mock.patch('uuid.uuid4', new=self.uuid):
            view.update()
        self.assertEqual(['2', '3', '4', '5', '6', '7', '8', '9'],
                         view.context.keys())

    def test_update_should_trigger_reload_of_body(self):
        view = self.get_view()
        view.request.form['paragraphs'] = []
        view.request.form['text'] = []
        view.update()
        view.url.assert_called_with(view.context, '@@contents')
        self.assertEqual(
            [{'args': ('editable-body', view.url.return_value),
              'name': 'reload',
              'when': None}],
            view.signals)

    def test_unknown_factories_are_mapped_to_p(self):
        view = self.get_view()
        view.request.form['paragraphs'] = ['2', '3']
        view.request.form['text'] = [
            dict(factory='iaminvalid', text='Hinter')]
        with mock.patch('uuid.uuid4', new=self.uuid):
            view.update()
        self.assertEqual('p', view.context['7'].type)

    def test_wild_html_should_be_munged_into_paragraph(self):
        view = self.get_view()
        view.request.form['paragraphs'] = ['2', '3']
        view.request.form['text'] = [{'text': u'\n<h3 class="supertitle"><a href="http://www.zeit.de/gesellschaft/zeitgeschehen/2010-12/asasange-festnahme-grossbritannien" title="Vergewaltigungsverdacht - Britische Polizei verhaftet Julian Assange">Vergewaltigungsverdacht</a></h3>\n<h4 class="title"><a href="http://www.zeit.de/gesellschaft/zeitgeschehen/2010-12/asasange-festnahme-grossbritannien" title="Vergewaltigungsverdacht - Britische Polizei verhaftet Julian Assange" rel="bookmark">Britische Polizei verhaftet Julian Assange</a></h4>\n<p>Julian Assange wollte sich "freiwillig" mit der britischen Polizei \ntreffen, doch jetzt klickten die Handschellen. Der untergetauchte \nWikileaks-Gr\xfcnder wurde verhaftet.&nbsp;\n\t    <a href="http://www.zeit.de/gesellschaft/zeitgeschehen/2010-12/asasange-festnahme-grossbritannien" class="more-link" rel="no-follow" title="Vergewaltigungsverdacht - Britische Polizei verhaftet Julian Assange">[weiter\u2026]</a></p>\n', 'factory': 'div'}, {'text': '\n<a><strong></strong></a>', 'factory': 'p'}]
        with mock.patch('uuid.uuid4', new=self.uuid):
            view.update()
        self.assertEqual('p', view.context['7'].type)


class TestTextEditing(
    zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(TestTextEditing, self).setUp()
        self.add_article()

    def test_paragraph_etc_should_not_appear_as_modules(self):
        s = self.selenium
        s.assertElementNotPresent('css=.block.type-p')
        s.click('link=Module')
        s.waitForElementPresent('css=#article-modules .module:contains(Video)')
        s.assertElementNotPresent('css=#article-modules .module:contains(<p>)')

    def test_clicking_empty_paragraph_at_end_should_create_paragraph(self):
        s = self.selenium
        s.assertElementNotPresent('css=.block.type-p')
        s.waitForElementPresent('css=.create-paragraph')
        s.click('css=.create-paragraph')
        s.waitForElementPresent('css=.block.type-p')

    @unittest2.skip("no typeKeys 'til webdriver")
    def test_typed_text_should_be_saved(self):
        s = self.selenium
        self.create()
        # Due to a bug in selenium, the letter 'y' will send the key code for
        # ALT. Thus we have to avoid passing typeKeys sentences containing 'y'.
        s.typeKeys('css=.block.type-p .editable p', 'Saskia had a little pig.')
        self.save()
        s.waitForElementPresent('css=.editable p:contains(Saskia had)')

    def test_class_attributes_should_be_removed_on_keyup(self):
        s = self.selenium
        self.create("<h4 class='title'>blubbel</h4>")
        s.assertElementPresent('css=.block.type-p h4.title:contains(blubbel)')
        s.fireEvent('css=.block.type-p .editable', 'keyup')
        s.assertElementNotPresent(
            'css=.block.type-p h4.title:contains(blubbel)')

    def test_style_attributes_should_be_removed_on_keyup(self):
        s = self.selenium
        self.create("<h4 style='display: inline'>blubbel</h4>")
        s.assertElementPresent('css=.block.type-p h4[style]')
        s.fireEvent('css=.block.type-p .editable', 'keyup')
        s.assertElementNotPresent('css=.block.type-p h4[style]')

    def test_consequent_paragraphs_should_be_editable_together(self):
        s = self.selenium
        self.create('<p>foo</p><p>bar</p>')
        self.save()
        s.waitForCssCount('css=.block.type-p', 2)
        s.click('css=.block.type-p .editable')
        s.assertCssCount('css=.block.type-p', 1)
        s.assertCssCount('css=.block.type-p .editable > *', 2)

    @unittest2.skip("no typeKeys 'til webdriver")
    def test_newline_should_create_paragraph(self):
        s = self.selenium
        self.create()
        s.typeKeys('css=.block.type-p .editable p', 'First paragraph.')
        s.click('xpath=//a[@href="formatBlock/h3"]')
        s.keyPress('css=.block.type-p .editable h3', '13')
        s.typeKeys('css=.block.type-p .editable h3', 'Second paragraph.')
        s.waitForElementPresent('css=.editable p:contains(Second paragraph)')

    def test_editing_should_end_on_content_drag(self):
        self.selenium.windowMaximize()
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
        s.dragAndDrop('css=#breadcrumbs li:last a', '+100,+0')
        time.sleep(0.25)
        # Saved, no longer ediable
        s.waitForElementNotPresent('css=.block.type-p.editing')

    def test_create_paragraph_should_be_hidden_while_editing(self):
        s = self.selenium
        s.waitForElementPresent('css=.create-paragraph')
        s.click('css=.create-paragraph')
        s.waitForElementNotPresent('css=.create-paragraph')


class TestEditingMultipleParagraphs(
    zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(TestEditingMultipleParagraphs, self).setUp()
        from zeit.cms.checkout.helper import checked_out
        from zeit.edit.interfaces import IElementFactory
        from zeit.content.article.article import Article
        from zeit.content.article.interfaces import IArticle
        from zeit.content.article.edit.interfaces import IEditableBody

        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                self.repository['article'] = Article()
                with checked_out(self.repository['article']) as co:
                    zeit.cms.browser.form.apply_default_values(
                        co, IArticle)
                    co.year = 2010
                    co.ressort = u'International'
                    co.title = 'foo'
                    body = IEditableBody(co)
                    p_factory = zope.component.getAdapter(
                        body, IElementFactory, 'p')
                    img_factory = zope.component.getAdapter(
                        body, IElementFactory, 'image')
                    paragraph = p_factory()
                    paragraph.text = 'foo'
                    img_factory()
                    paragraph = p_factory()
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
        s.keyDown(second_p, '\\38')
        s.keyUp(second_p, '\\38')
        s.waitForEval(
            'selenium.browserbot.getCurrentWindow()'
            '.getSelection().getRangeAt(0).startOffset', '3')

    def test_arrow_down_moves_across_non_text_block_and_places_cursor_at_start(
        self):
        s = self.selenium
        first_p = 'css=.block.type-p .editable p'
        s.waitForElementPresent(first_p)
        s.click(first_p)
        s.keyDown(first_p, '\\40')
        s.keyUp(first_p, '\\40')
        s.waitForEval(
            'selenium.browserbot.getCurrentWindow()'
            '.getSelection().getRangeAt(0).startOffset', '0')


class TestLinkEditing(
    zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(TestLinkEditing, self).setUp()
        self.selenium.windowMaximize()
        self.add_article()

    def select_text(self):
        s = self.selenium
        self.create('<p>I want to link something</p>'
                    '<p>And I need distance<p>'
                    '<p>from the bottom landing zone<p>')
        s.getEval("""(function(s) {
            var p = s.browserbot.findElement('css=.block.type-p .editable p');
            var range = window.getSelection().getRangeAt(0);
            range.setStart(p.firstChild, 10);
            range.setEnd(p.firstChild, 14);
        })(this);""")
        s.assertElementNotPresent('xpath=//a[@href="http://example.com/"]')

    def select_link(self, additional=''):
        s = self.selenium
        self.create(
            ('<p>I want to <a href="http://example.com/" {0}>link</a> '
             'something</p>').format(additional))
        s.getEval("""(function(s) {
            var p = s.browserbot.findElement('css=.block.type-p .editable p');
            var range = window.getSelection().getRangeAt(0);
            range.setStart(p, 1);
            range.setEnd(p, 2);
        })(this);""")
        s.assertElementPresent('xpath=//a[@href="http://example.com/"]')

    def test_links_should_be_addable(self):
        s = self.selenium
        self.select_text()
        s.click('xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input input[name=href]')
        s.type('css=.link_input input[name=href]', 'http://example.com/')
        s.click('css=.link_input button[name=insert_link_ok]')
        s.waitForElementPresent('xpath=//a[@href="http://example.com/"]')

    def test_target_should_be_editable(self):
        s = self.selenium
        self.select_text()
        s.click('xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input input[name=href]')
        s.select('css=.link_input select[name=target]', 'label=Neues Fenster')
        s.type('css=.link_input input[name=href]', 'http://example.com/')
        s.click('css=.link_input button[name=insert_link_ok]')
        s.waitForElementPresent(
            'xpath=//a[@href="http://example.com/" and @target="_blank"]')

    def test_edit_on_link_should_set_href_in_input(self):
        s = self.selenium
        self.select_link()
        s.click('xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input input[name=href]')
        s.assertValue(
            'css=.link_input input[name=href]', 'http://example.com/')

    def test_edit_on_link_should_set_target_to_select(self):
        s = self.selenium
        self.select_link(additional='target="_blank"')
        s.click('xpath=//a[@href="insert_link"]')
        s.waitForVisible('css=.link_input input[name=href]')
        s.assertSelectedLabel(
            'css=.link_input select[name=target]', 'Neues Fenster')

    def test_edit_should_highlight_link_being_edited(self):
        s = self.selenium
        self.select_text()
        s.click('xpath=//a[@href="insert_link"]')
        s.assertElementPresent('css=.editable a.link-edit')

    def test_links_should_be_removable(self):
        s = self.selenium
        self.select_link()
        s.click('xpath=//a[@href="unlink"]')
        s.waitForElementNotPresent('xpath=//a[@href="http://example.com/"]')

    def test_cancel_should_keep_selection(self):
        s = self.selenium
        self.select_text()
        s.click('xpath=//a[@href="insert_link"]')
        s.waitForElementPresent('css=.editable a')
        s.click('css=.link_input button[name=insert_link_cancel]')
        result = s.getEval("""(function(s) {
            var range = window.getSelection().getRangeAt(0);
            return range.startContainer.childNodes[range.startOffset].data
        })(this);""")
        self.assertEqual(u'link', result)

    def test_insert_link_should_select_link(self):
        s = self.selenium
        self.select_text()
        s.click('xpath=//a[@href="insert_link"]')
        s.type('css=.link_input input[name=href]', 'http://example.com/')
        s.click('css=.link_input button[name=insert_link_ok]')
        s.waitForElementPresent('xpath=//a[@href="http://example.com/"]')
        result = s.getEval("""(function(s) {
            var range = window.getSelection().getRangeAt(0);
            return range.startContainer.childNodes[range.startOffset].nodeName;
        })(this);""")
        self.assertEqual('A', result)

    def test_edit_link_with_cancel_should_keep_link_selected(self):
        s = self.selenium
        self.select_link()
        s.click('xpath=//a[@href="insert_link"]')
        s.click('css=.link_input button[name=insert_link_cancel]')
        result = s.getEval("""(function(s) {
            var range = window.getSelection().getRangeAt(0);
            return range.startContainer.childNodes[range.startOffset].nodeName;
        })(this);""")
        self.assertEqual('A', result)

    def test_cancel_should_not_insert_link(self):
        s = self.selenium
        self.select_text()
        s.click('xpath=//a[@href="insert_link"]')
        s.waitForElementPresent('css=.editable a')
        s.click('css=.link_input button[name=insert_link_cancel]')
        s.waitForElementNotPresent('css=.editable a')

    def test_dialog_should_accept_content_drop(self):
        s = self.selenium
        self.select_text()
        s.click('xpath=//a[@href="insert_link"]')
        # We need to scroll the inner "frame" to top, otherwise dragging will
        # get confused:
        s.getEval(
            "this.browserbot.findElement('css=.diver-bar')."
            "   scrollIntoView(true)")
        s.dragAndDropToObject(
            'css=#breadcrumbs li:last a', 'css=.link_input')
        s.assertValue(
            'css=.link_input input[name=href]', 'http://www.zeit.de/*.tmp')

    def test_drag_while_dialog_open_should_not_end_edit(self):
        s = self.selenium
        self.select_text()
        s.click('xpath=//a[@href="insert_link"]')
        s.dragAndDrop('css=#breadcrumbs li:last a', '+100,+0')
        time.sleep(0.25)
        # Element still there
        s.assertElementPresent('css=.block.type-p.editing')


class TestFolding(
    zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(TestFolding, self).setUp()
        self.add_article()

    def assert_foldable(self, block):
        s = self.selenium
        self.create_block(block)
        s.assertElementNotPresent('css=.block.type-{0}.folded'.format(block))
        s.click('css=.block.type-{0} .edit-bar .fold-link'.format(block))
        s.waitForElementPresent('css=.block.type-{0}.folded'.format(block))
        s.click('css=.block.type-{0} .edit-bar .fold-link'.format(block))
        s.waitForElementNotPresent('css=.block.type-{0}.folded'.format(block))

    def test_audio_should_be_foldable(self):
        self.assert_foldable('audio')

    def test_image_should_be_foldable(self):
        self.assert_foldable('image')

    def test_gallery_should_be_foldable(self):
        self.assert_foldable('gallery')

    def test_citation_should_be_foldable(self):
        self.assert_foldable('citation')

    def test_infobox_should_be_foldable(self):
        self.assert_foldable('infobox')

    def test_portraitbox_should_be_foldable(self):
        self.assert_foldable('portraitbox')

    def test_relateds_should_be_foldable(self):
        self.assert_foldable('relateds')

    def test_raw_should_be_foldable(self):
        self.assert_foldable('raw')

    def test_video_should_be_foldable(self):
        self.assert_foldable('video')


class TestReadonlyVisible(unittest2.TestCase,
                 zeit.cms.testing.BrowserAssertions):

    layer = zeit.content.article.testing.TestBrowserLayer

    def create_block(self, block):
        from zeit.content.article.article import Article
        article = Article()
        article.xml.body.division = ''
        article.xml.body.division.set('type', 'page')
        article.xml.body.division[block] = ''
        root = self.layer.setup.getRootFolder()
        with zeit.cms.testing.site(root):
            with zeit.cms.testing.interaction():
                root['repository']['article'] = article
        from zope.testbrowser.testing import Browser
        browser = Browser()
        browser.addHeader('Authorization', 'Basic user:userpw')
        browser.open(
            'http://localhost:8080/++skin++vivi/repository/article/@@contents')
        return browser

    def assert_visible(self, block):
        browser = self.create_block(block)
        self.assert_ellipsis(
            '...<div ...class="block type-{0}...'.format(block),
            browser.contents)

    def test_raw_xml_should_be_visible_in_readonly_mode(self):
        self.assert_visible('raw')

    def test_audio_should_be_visible_in_readonly_mode(self):
        self.assert_visible('audio')

    def test_citation_should_be_visible_in_readonly_mode(self):
        self.assert_visible('citation')

    def test_relateds_should_be_visible_in_readonly_mode(self):
        self.assert_visible('relateds')

    def test_landing_zone_after_block_should_not_be_visible(self):
        browser = self.create_block('raw')
        self.assertNotIn('landing-zone', browser.contents)

    def test_blocks_should_not_be_sortable(self):
        browser = self.create_block('raw')
        self.assertNotIn('action-block-sorter', browser.contents)


class TestDivision(
    zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(TestDivision, self).setUp()
        self.add_article()

    def create_division(self):
        s = self.selenium
        s.assertElementNotPresent('css=.block.type-division')
        s.click('link=Module')
        s.waitForElementPresent(
            'css=#article-modules .module[cms\\:block_type=division]')
        s.dragAndDropToObject(
            'css=#article-modules .module[cms\\:block_type=division]',
            'css=#article-editor-text .landing-zone.visible')
        s.waitForElementPresent('css=.block.type-division')

    def test_division_should_have_editable_teaser(self):
        self.create_division()
        s = self.selenium
        s.waitForElementPresent('css=.type-division input')
        s.type('css=.type-division input', 'Division teaser')
        s.fireEvent('css=.type-division input', 'blur')
        s.waitForElementNotPresent('css=.field.dirty')
        # Re-open the page and verify that the data is still there
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent('css=.type-division input')
        s.assertValue('css=.type-division input', 'Division teaser')


class TestLimitedInput(
    zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(TestLimitedInput, self).setUp()
        self.add_article()

    @unittest2.skip("no typeKeys 'til webdriver")
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
        super(TestCountedInput, self).setUp()
        self.add_article()

    @unittest2.skip("no typeKeys 'til webdriver")
    def test_input_should_be_counted_on_input(self):
        s = self.selenium
        s.waitForElementPresent('xpath=//span[@class="charlimit"]')
        s.assertText('xpath=//span[@class="charcount"]', '0 Zeichen')
        self.create()
        s.typeKeys('css=.block.type-p .editable p', 'Saskia had a little pig')
        self.save()
        s.assertText('xpath=//span[@class="charcount"]', '23 Zeichen')

    @unittest2.skip("no typeKeys 'til webdriver")
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


class TestDummyAd(zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(TestDummyAd, self).setUp()
        self.add_article()
        from zope.testbrowser.testing import Browser
        import json
        browser = Browser()
        browser.addHeader('Authorization', 'Basic user:userpw')
        browser.open(
            'http://localhost:8080/++skin++vivi/@@banner-rules')
        self.rules = json.loads(browser.contents)

    @unittest2.skip("no typeKeys 'til webdriver")
    def test_dummy_ad_should_be_rendered_on_banner_rules(self):
        style = ''
        for r in self.rules:
            style += 'p:nth-child\(' + str(r) + '\).*background:.*dummy-ad'
        s = self.selenium
        self.create()
        s.typeKeys('css=.block.type-p .editable p', 'First paragraph.')
        s.keyPress('css=.block.type-p .editable p', '13')
        s.typeKeys('css=.block.type-p .editable p', 'Second paragraph.')
        s.waitForElementPresent('css=.editable p:contains(Second paragraph)')
        s.assertText('css=#content_editable_hacks', 'regex:' + style)
