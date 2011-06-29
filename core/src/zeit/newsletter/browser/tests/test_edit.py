# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.newsletter.testing
import zope.component


class EditorTest(zeit.newsletter.testing.BrowserTestCase):

    def setUp(self):
        from zeit.newsletter.newsletter import Newsletter
        super(EditorTest, self).setUp()
        self.repository['newsletter'] = Newsletter()

    def test_newsletter_can_be_checked_out(self):
        self.browser.handleErrors = False
        self.browser.open(
            'http://localhost/++skin++vivi/repository/newsletter/@@checkout')


class BlockEditingTest(zeit.newsletter.testing.SeleniumTestCase):

    log_errors = True

    def setUp(self):
        from zeit.newsletter.newsletter import Newsletter
        super(BlockEditingTest, self).setUp()
        with zeit.cms.testing.site(self.getRootFolder()):
            self.repository = zope.component.getUtility(
                zeit.cms.repository.interfaces.IRepository)
            self.repository['newsletter'] = Newsletter()
        self.open('/repository/newsletter/@@checkout')

    def test_groups_should_be_addable(self):
        s = self.selenium
        s.assertElementNotPresent('css=.block.type-group')
        s.waitForElementPresent('link=*Add group')
        s.click('link=*Add group')
        s.waitForElementPresent('css=.block.type-group')
