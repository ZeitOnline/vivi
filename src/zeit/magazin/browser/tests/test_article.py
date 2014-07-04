# coding: utf-8
# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.content.article.edit.browser.testing
import zeit.magazin.testing


class ArticleTemplateTest(
        zeit.content.article.edit.browser.testing.EditorHelper,
        zeit.cms.testing.SeleniumTestCase):

    layer = zeit.magazin.testing.SELENIUM_LAYER

    def setUp(self):
        super(ArticleTemplateTest, self).setUp()
        self.add_article('/repository/magazin')
        self.selenium.waitForElementPresent('id=options-zmo.template')

    def test_changing_template_should_update_header_layout_list(self):
        s = self.selenium
        s.click('css=#edit-form-misc .edit-bar .fold-link')

        s.assertSelectedLabel('id=options-zmo.template', '(nothing selected)')
        s.assertNotVisible('css=.fieldname-header_layout')
        s.select('id=options-zmo.template', 'Kolumne')
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
            s.getSelectOptions('id=options-zmo.header_layout'))
        s.click('options-zmo.actions.apply')
        s.pause(250)
        self.assertEqual(
            kolumne_layouts,
            s.getSelectOptions('id=options-zmo.header_layout'))
