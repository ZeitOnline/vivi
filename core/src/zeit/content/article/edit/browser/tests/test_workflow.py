# coding: utf-8
# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.article.article import Article
import mock
import zeit.cms.testing
import zeit.content.article.testing


class Checkin(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.ArticleLayer

    def test_validation_errors_should_be_displayed_at_checkin_button(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                self.repository['article'] = Article()
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/article/@@checkout')
        b.open('@@edit.form.checkin')
        self.assert_ellipsis('...Title:...Required input is missing...')
        self.assertTrue(b.getControl('Save').disabled)

    def test_checkin_does_not_set_last_semantic_change_by_default(self):
        b = self.browser
        b.handleErrors = False
        b.open('http://localhost/++skin++vivi/repository/'
               'online/2007/01/Somalia/@@checkout')
        with mock.patch(
            'zeit.cms.checkout.browser.manager.Checkin.__call__') as checkin:
            checkin.return_value = None
            b.open('@@edit.form.checkin')
            b.getControl('Save').click()
            checkin.assert_called_with(semantic_change=False)

    def test_checkin_sets_last_semantic_change_if_checked(self):
        b = self.browser
        b.handleErrors = False
        b.open('http://localhost/++skin++vivi/repository/'
               'online/2007/01/Somalia/@@checkout')
        with mock.patch(
            'zeit.cms.checkout.browser.manager.Checkin.__call__') as checkin:
            checkin.return_value = None
            b.open('@@edit.form.checkin')
            b.getControl(name='semantic_change').controls[0].selected = True
            b.getControl('Save').click()
            checkin.assert_called_with(semantic_change=True)


class CheckinJS(zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_checkin_redirects_to_repository(self):
        s = self.selenium
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        s.waitForElementPresent('name=checkin')
        self.assertNotIn('repository', s.getLocation())
        s.clickAndWait('name=checkin')
        self.assertIn('repository', s.getLocation())
