# coding: utf-8
# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.article.article import Article
import zeit.cms.testing
import zeit.content.article.testing


class CheckinValidationTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.ArticleLayer

    def test_validation_errors_should_be_displayed_at_checkin_button(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                self.repository['article'] = Article()
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/article/@@checkout')
        b.open('@@edit.form.checkin')
        self.assert_ellipsis('...Title:...Required input is missing...')
