# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import zeit.content.article.testing


class SaveTextTest(zeit.content.article.testing.FunctionalTestCase):

    def get_view(self, body=None):
        from zeit.content.article.edit.browser.edit import SaveText
        import lxml.objectify
        import zeit.content.article.article
        import zeit.content.article.edit.body
        if not body:
            body  = ("<division><p>Para 1</p><p>Para 2</p></division>"
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

    def test_update_should_map_h3_to_intertitle(self):
        view = self.get_view()
        view.request.form['paragraphs'] = ['2', '3']
        view.request.form['text'] = [
            dict(factory='h3', text='Hinter')]
        with mock.patch('uuid.uuid4', new=self.uuid):
            view.update()
        self.assertEqual('intertitle', view.context['7'].type)

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


class TestTextEditing(zeit.content.article.testing.SeleniumTestCase):

    def setUp(self):
        super(TestTextEditing, self).setUp()
        s = self.selenium
        self.open('/repository')
        s.select('id=add_menu', 'label=Article')
        s.waitForPageToLoad()

    def create(self, contents=None):
        s = self.selenium
        s.assertElementNotPresent('css=.block.type-p')
        s.waitForElementPresent('link=Create paragraph')
        s.click('link=Create paragraph')
        s.waitForElementPresent('css=.block.type-p')
        s.click('css=.block.type-p .editable')
        if contents:
            s.getEval(
                "this.browserbot.findElement("
                "  'css=.block.type-p .editable').innerHTML = '{0}'".format(
                    contents.replace("'", "\\'")))

    def save(self, locator='css=.block.type-p .editable'):
        self.selenium.getEval(
            "window.MochiKit.Signal.signal("
            "   this.browserbot.findElement('{0}'), 'save')".format(locator))
        self.selenium.waitForElementNotPresent('xpath=//*[@contenteditable]')

    def test_landing_zone_should_take_modules(self):
        s = self.selenium
        s.assertElementNotPresent('css=.block.type-p')
        s.click('link=Module')
        s.waitForElementPresent('css=#article-modules .module:contains(<p>)')
        s.dragAndDropToObject(
            'css=#article-modules .module:contains(<p>)',
            'css=#article-editor-text .landing-zone.visible')
        s.waitForElementPresent('css=.block.type-p')

    def test_create_paragraph_link_should_create_paragraph(self):
        s = self.selenium
        s.assertElementNotPresent('css=.block.type-p')
        s.waitForElementPresent('link=Create paragraph')
        s.click('link=Create paragraph')
        s.waitForElementPresent('css=.block.type-p')

    def test_typed_text_should_be_saved(self):
        s = self.selenium
        self.create()
        s.typeKeys('css=.block.type-p .editable p', 'Mary had a little lamb.')
        self.save()
        s.waitForElementPresent('css=.editable p:contains(Mary had)')

    def test_text_nodes_should_become_paragraphs(self):
        s = self.selenium
        self.create()
        s.getEval("this.browserbot.findElement("
                  "  'css=.block.type-p .editable').innerHTML = "
                  "   'Mary<p>had a little</p>'")
        self.save()
        s.waitForElementPresent('css=.editable p:contains(Mary)')

    def test_top_level_inline_styles_should_be_joined_to_paragraph(self):
        s = self.selenium
        self.create()
        s.getEval("this.browserbot.findElement("
                  "  'css=.block.type-p .editable').innerHTML = "
                  "   'Mary <strong>had</strong> a little lamb.'")
        self.save()
        s.waitForElementPresent('css=.editable p:contains(Mary had a)')
        s.assertElementPresent('css=.editable p > strong:contains(had)')

    def test_top_level_inline_styles_should_not_joined_to_existing_p(self):
        s = self.selenium
        self.create()
        s.getEval(
            "this.browserbot.findElement("
            " 'css=.block.type-p .editable').innerHTML = "
            " '<p>foo</p>Mary <strong>had</strong> a little lamb. <p>bar</p>'")
        self.save()
        s.waitForElementPresent('css=.editable p:contains(Mary had a)')
        s.assertElementPresent('css=.editable p > strong:contains(had)')
        s.assertElementNotPresent('css=.editable p:contains(foo Mary)')
        s.assertElementNotPresent('css=.editable p:contains(lamb. bar)')

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

    def test_links_should_be_addable(self):
        s = self.selenium
        self.create('<p>I want to link something</p>')
        s.getEval("""(function(s) {
            var p = s.browserbot.findElement('css=.block.type-p .editable p');
            var range = window.getSelection().getRangeAt(0);
            range.setStart(p.firstChild, 10);
            range.setEnd(p.firstChild, 14);
        })(this);""")
        s.assertElementNotPresent('xpath=//a[@href="http://example.com/"]')
        s.answerOnNextPrompt('http://example.com/')
        s.click('xpath=//a[@href="insert_link"]')
        s.waitForElementPresent('xpath=//a[@href="http://example.com/"]')

    def test_links_should_be_removable(self):
        s = self.selenium
        self.create('<p>I want to <a href="http://example.com/">link</a> '
                    'something</p>')
        s.getEval("""(function(s) {
            var p = s.browserbot.findElement('css=.block.type-p .editable p');
            var range = window.getSelection().getRangeAt(0);
            range.setStart(p, 1);
            range.setEnd(p, 2);
        })(this);""")
        s.assertElementPresent('xpath=//a[@href="http://example.com/"]')
        s.click('xpath=//a[@href="unlink"]')
        s.waitForElementNotPresent('xpath=//a[@href="http://example.com/"]')
