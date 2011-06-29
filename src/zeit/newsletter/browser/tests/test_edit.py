# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.newsletter.testing


class EditorTest(zeit.newsletter.testing.BrowserTestCase):

    def setUp(self):
        from zeit.newsletter.newsletter import Newsletter
        super(EditorTest, self).setUp()
        self.repository['newsletter'] = Newsletter()

    def test_newsletter_can_be_checked_out(self):
        self.browser.handleErrors = False
        self.browser.open(
            'http://localhost/++skin++vivi/repository/newsletter/@@checkout')
