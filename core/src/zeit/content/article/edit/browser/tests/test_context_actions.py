# coding: utf8
# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.content.article.testing


class WorkingcopyTest(zeit.content.article.testing.SeleniumTestCase):

    def setUp(self):
        from zeit.content.article.interfaces import IArticle
        import transaction
        import zeit.cms.browser.form
        super(WorkingcopyTest, self).setUp()
        self.open('/repository/online/2007/01/Somalia/')
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        article = self.getRootFolder()[
            'workingcopy']['zope.user']['Somalia']
        with zeit.cms.testing.site(self.getRootFolder()):
            zeit.cms.browser.form.apply_default_values(article, IArticle)
        transaction.commit()
        self.open(self.selenium.getLocation())
        self.selenium.waitForElementPresent('id=checkin')

    def test_article_should_be_checked_in(self):
        s = self.selenium
        s.clickAndWait('id=checkin')
        s.assertElementNotPresent('id=checkin')

    def test_workingcopy_should_be_removable(self):
        s = self.selenium
        s.click('id=delete_workingcopy')
        s.waitForElementPresent('xpath=//input[@value="Delete"]')
        s.assertTextPresent('Do you really want to delete your workingcopy?')
        s.clickAndWait('form.actions.delete')
