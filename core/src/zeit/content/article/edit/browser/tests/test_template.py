# coding: utf8
import zeit.content.article.edit.browser.testing


class ArticleTemplateTest(
        zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(ArticleTemplateTest, self).setUp()
        self.add_article()
        self.selenium.waitForElementPresent('id=options-template.template')

    def test_changing_template_should_update_header_layout_list(self):
        s = self.selenium
        s.click('css=#edit-form-misc .edit-bar .fold-link')

        s.assertSelectedLabel(
            'id=options-template.template', 'Artikel')
        s.select('id=options-template.template', 'Kolumne')
        s.pause(100)

        kolumne_layouts = [
            u'(nothing selected)',
            u'Heiter bis glücklich',
            u'Ich habe einen Traum',
            u'Martenstein',
            u'Standard',
            u'Von A nach B',
        ]

        s.assertVisible('css=.fieldname-header_layout')
        self.assertEqual(
            kolumne_layouts,
            s.getSelectOptions('id=options-template.header_layout'))
        s.type('id=options-template.header_layout', '\t')
        s.pause(500)
        self.assertEqual(
            kolumne_layouts,
            s.getSelectOptions('id=options-template.header_layout'))
