# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.newsletter.testing
import zope.testbrowser.testing
import unittest2 as unittest


class EditorTest(unittest.TestCase,
                 zeit.cms.testing.BrowserAssertions):

    layer = zeit.newsletter.testing.TestBrowserLayer

    def setUp(self):
        from zeit.newsletter.newsletter import Newsletter
        import zeit.cms.repository.interfaces
        super(EditorTest, self).setUp()
        self.browser = zope.testbrowser.testing.Browser()
        self.browser.addHeader('Authorization', 'Basic user:userpw')
        with zeit.cms.testing.site(self.layer.setup.getRootFolder()):
            repository = zope.component.getUtility(
                zeit.cms.repository.interfaces.IRepository)
            repository['newsletter'] = Newsletter()

    def test_newsletter_can_be_checked_out(self):
        self.browser.handleErrors = False
        self.browser.open(
            'http://localhost/++skin++vivi/repository/newsletter/@@checkout')
