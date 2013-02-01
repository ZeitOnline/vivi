# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.article.article import Article
import zeit.cms.testing
import zeit.content.article.testing


class BadgeWidget(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.ArticleLayer

    def test_shows_labels_in_display_mode(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                self.repository['article'] = Article()
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/article/@@edit.form.asset-badges?show_form=1')
        # just looking for any label is not enough, since each widget begins
        # with one
        self.assertEllipsis('...<label cms:tooltip="Video"...', b.contents)

    def test_labels_have_tooltip_in_input_mode(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                self.repository['article'] = Article()
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/article/@@checkout')
        b.open('@@edit.form.asset-badges?show_form=1')
        self.assertEllipsis('...<label cms:tooltip="Video"...', b.contents)

    def test_renders_selected_items(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                self.repository['article'] = Article()
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/article/@@checkout')
        b.open('@@edit.form.asset-badges?show_form=1')
        b.getControl(name='asset-badges.badges').controls[0].selected = True
        b.getControl('Apply').click()
        b.open('@@edit.form.asset-badges?show_form=1')
        self.assertTrue(
            b.getControl(name='asset-badges.badges').controls[0].selected)
