# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest2
import zeit.content.article.edit.browser.testing
import zeit.content.article.testing


def css_path(css):
    import lxml.cssselect
    return lxml.cssselect.CSSSelector(css).path


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


class TestTextEditing(
    zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(TestTextEditing, self).setUp()
        self.add_article()

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

    def test_consequent_paragraphs_should_be_editable_together(self):
        s = self.selenium
        s.assertElementNotPresent('css=.block.type-p')
        s.waitForElementPresent('link=Create paragraph')
        s.click('link=Create paragraph')
        s.waitForElementPresent('css=.block.type-p')
        s.click('link=Create paragraph')
        s.waitForXpathCount(css_path('.block.type-p'), 2)
        s.click('css=.block.type-p .editable')
        s.assertXpathCount(css_path('.block.type-p'), 1)
        s.assertXpathCount(css_path('.block.type-p .editable > *'), 2)

    def test_joined_paragraphs_should_be_movable_together_while_edited(
        self):
        s = self.selenium
        # Prepare content: p, p, division, p, p
        s.assertElementNotPresent('css=.block.type-p')
        s.waitForElementPresent('link=Create paragraph')
        s.click('link=Create paragraph')
        s.waitForElementPresent('css=.block.type-p')
        s.click('link=Create paragraph')
        s.waitForXpathCount(css_path('.block.type-p'), 2)
        s.click('link=Module')
        s.waitForElementPresent('css=#article-modules .module')
        s.dragAndDropToObject(
            'css=#article-modules .module[cms\\:block_type=division]',
            'css=#article-editor-text .landing-zone.visible')
        s.waitForElementPresent('css=.block.type-division')
        s.click('link=Create paragraph')
        s.waitForXpathCount(css_path('.block.type-p'), 3)
        s.click('link=Create paragraph')
        s.waitForXpathCount(css_path('.block.type-p'), 4)
        # Start editing
        s.click('css=.block.type-p .editable')
        height = s.getElementHeight('css=.block.type-p')
        s.click('css=.block.type-p .dragger')
        s.dragAndDrop('css=.block.type-p .dragger',
                      '0,{0}'.format(height*2))

    def _skip_test_action_links_should_be_hidden_while_editing(self):
        s = self.selenium
        s.waitForElementPresent('link=Create paragraph')
        s.click('link=Create paragraph')
        s.waitForElementPresent('css=.block.type-p')
        # XXX The delete link is only visible while hovering above the block;
        # I haven't been able to simulate that with Selenium, though.
        s.mouseOver('css=.block')
        s.assertVisible('css=.block a.delete-link')
        s.click('css=.block.type-p .editable')
        s.mouseOver('css=.block')
        s.waitForNotVisible('css=.block a.delete-link')

    def _skip_test_lock_should_always_be_released(self):
        # XXX we can't even get a setup with two paragraphs. Sigh.
        s = self.selenium
        s.waitForElementPresent('link=Create paragraph')
        s.click('link=Create paragraph')
        p1 = 'css=.block.type-p .editable'
        p2 = 'css=.block.type-p + .landing-zone + .block.type-p .editable'
        self.create('<p>first</p><p>second</p>')
        self.save()
        s.waitForElementPresent(p2)
        s.click(p1)
        s.click(p2)
        self.save()
        s.click(p1)
        s.waitForElementPresent('xpath=//*[@contenteditable]')


class TestFolding(
    zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(TestFolding, self).setUp()
        self.add_article()

    def assert_foldable(self, block):
        s = self.selenium
        s.click('link=Module')
        s.waitForElementPresent('css=#article-modules .module')
        s.dragAndDropToObject(
            'css=#article-modules .module[cms\\:block_type={0}]'.format(block),
            'css=#article-editor-text .landing-zone.visible')
        s.waitForElementPresent('css=.block.type-{0}'.format(block))
        s.assertElementNotPresent('css=.block.type-{0}.folded'.format(block))
        s.click('css=.block.type-{0} .edit-bar .fold-link'.format(block))
        s.waitForElementPresent('css=.block.type-{0}.folded'.format(block))
        s.click('css=.block.type-{0} .edit-bar .fold-link'.format(block))
        s.waitForElementNotPresent('css=.block.type-{0}.folded'.format(block))

    def assert_fold_survives_page_load(self, block):
        s = self.selenium
        s.click('link=Module')
        s.waitForElementPresent('css=#article-modules .module')
        s.dragAndDropToObject(
            'css=#article-modules .module[cms\\:block_type={0}]'.format(block),
            'css=#article-editor-text .landing-zone.visible')
        s.waitForElementPresent('css=.block.type-{0}'.format(block))
        s.assertElementNotPresent('css=.block.type-{0}.folded'.format(block))
        s.click('css=.block.type-{0} .edit-bar .fold-link'.format(block))
        s.waitForElementPresent('css=.block.type-{0}.folded'.format(block))
        s.open(s.getLocation())
        s.waitForElementPresent('css=.block.type-{0}.folded'.format(block))

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

    def test_audio_should_survive_page_load(self):
        self.assert_fold_survives_page_load('audio')

    def test_image_should_survive_page_load(self):
        self.assert_fold_survives_page_load('image')

    def test_gallery_should_survive_page_load(self):
        self.assert_fold_survives_page_load('gallery')

    def test_citation_should_survive_page_load(self):
        self.assert_fold_survives_page_load('citation')

    def test_infobox_should_survive_page_load(self):
        self.assert_fold_survives_page_load('infobox')

    def test_portraitbox_should_survive_page_load(self):
        self.assert_fold_survives_page_load('portraitbox')

    def test_relateds_should_survive_page_load(self):
        self.assert_fold_survives_page_load('relateds')

    def test_raw_should_survive_page_load(self):
        self.assert_fold_survives_page_load('raw')

    def test_video_should_survive_page_load(self):
        self.assert_fold_survives_page_load('video')


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
        s.click('link=Edit')
        s.waitForElementPresent('id=form.teaser')
        s.type('id=form.teaser', "Division teaser")
        s.click('id=form.actions.apply')
        s.waitForTextPresent('Division teaser')
