# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.newsletter.category import NewsletterCategory
import datetime
import mock
import zeit.newsletter.testing


class AddTest(zeit.newsletter.testing.BrowserTestCase):

    def setUp(self):
        super(AddTest, self).setUp()
        with zeit.cms.testing.site(self.getRootFolder()):
            self.repository['mynl'] = NewsletterCategory()

    def test_adding_a_newsletter_should_check_out(self):
        b = self.browser
        dt = mock.Mock()
        dt.now.return_value = datetime.datetime(2011, 6, 29, 13, 30)

        with mock.patch('datetime.datetime', dt):
            b.open('http://localhost/++skin++vivi/repository/mynl/@@add')
        self.assertEqual(
            'http://localhost/++skin++vivi/workingcopy/zope.user'
            '/29-1/@@edit.html', b.url)
