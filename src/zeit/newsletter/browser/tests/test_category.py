# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.newsletter.category import NewsletterCategory
import datetime
import mock
import pytz
import transaction
import zeit.cms.repository.folder
import zeit.newsletter.testing


class AddTest(zeit.newsletter.testing.SeleniumTestCase):

    def setUp(self):
        super(AddTest, self).setUp()
        with zeit.cms.testing.site(self.getRootFolder()):
            self.repository['newsletter'] = zeit.cms.repository.folder.Folder()
            self.repository['newsletter']['taeglich'] = NewsletterCategory()
        transaction.commit()
        self.open('/')

    def test_adding_a_newsletter_should_check_out(self):
        dt = mock.Mock()
        dt.now.return_value = datetime.datetime(
            2011, 6, 29, 13, 30, tzinfo=pytz.UTC)

        s = self.selenium
        s.waitForElementPresent('sidebar.form.type_')
        s.select('sidebar.form.type_', 'Daily Newsletter')

        with mock.patch('datetime.datetime', dt):
            s.clickAndWait('sidebar.form.actions.add')
            s.assertLocation('*/workingcopy/zope.user/29-1/@@edit.html')
