import zeit.content.article.testing


class WorkingcopyTest(zeit.content.article.testing.SeleniumTestCase):
    def setUp(self):
        import transaction

        super().setUp()
        self.selenium.setTimeout(3600000)
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
        s.waitForElementPresent('id=delete_workingcopy')
        s.click('id=delete_workingcopy')
        s.waitForElementPresent('xpath=//input[@value="Confirm delete"]')
        s.assertTextPresent('Do you really want to delete your workingcopy?')
        s.clickAndWait('name=form.actions.delete')
