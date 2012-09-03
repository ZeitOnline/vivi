# coding: utf8
# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.article.testing


class WorkingcopyTest(zeit.content.article.testing.SeleniumTestCase):

    def setUp(self):
        import transaction
        super(WorkingcopyTest, self).setUp()
        self.open('/repository/online/2007/01/Somalia/')
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        transaction.commit()
        self.selenium.open(self.selenium.getLocation())
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
