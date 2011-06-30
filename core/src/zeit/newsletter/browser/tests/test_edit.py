# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import transaction
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

    def setUp(self):
        from zeit.newsletter.newsletter import Newsletter
        super(BlockEditingTest, self).setUp()
        with zeit.cms.testing.site(self.getRootFolder()):
            self.repository = zope.component.getUtility(
                zeit.cms.repository.interfaces.IRepository)
            self.repository['newsletter'] = Newsletter()
        self.open('/repository/newsletter/@@checkout')
        transaction.commit()

    def test_groups_should_be_addable(self):
        s = self.selenium
        s.assertElementNotPresent('css=.block.type-group')
        s.waitForElementPresent('link=*Add group')
        s.click('link=*Add group')
        s.waitForElementPresent('css=.block.type-group')

    def test_drag_content_to_group_should_create_teaser_block(self):
        self.create_content_and_fill_clipboard()
        self.test_groups_should_be_addable()
        s = self.selenium
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c3"]', 'css=div.type-group')
        s.waitForElementPresent('css=.block.type-teaser')
        s.assertText('css=.block.type-teaser', '*http://xml.zeit.de/c3*')

    def test_drag_content_to_teaser_should_append_teaser_block(self):
        self.create_content_and_fill_clipboard()
        self.test_groups_should_be_addable()
        s = self.selenium
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c3"]', 'css=div.type-group')
        s.waitForElementPresent('css=.block.type-teaser + .landing-zone')
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c1"]', 'css=div.type-teaser + .landing-zone')
        second_teaser = 'css=.type-teaser + * + .type-teaser'
        s.waitForElementPresent(second_teaser)
        s.assertText(second_teaser, '*http://xml.zeit.de/c1*')
