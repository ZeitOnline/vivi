from unittest import mock
from zeit.newsletter.category import NewsletterCategory
import datetime
import pytz
import transaction
import zeit.cms.repository.folder
import zeit.newsletter.testing


class AddTest(zeit.newsletter.testing.SeleniumTestCase):

    def setUp(self):
        super().setUp()
        self.repository['newsletter'] = zeit.cms.repository.folder.Folder()
        category = NewsletterCategory()
        category.subject = 'nosubject'
        self.repository['newsletter']['taeglich'] = category
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
            s.clickAndWait('name=sidebar.form.actions.add')
            s.waitForLocation('*/workingcopy/zope.user/29-1/@@edit.html')


class CategoryMetadata(zeit.newsletter.testing.BrowserTestCase):

    def setUp(self):
        super().setUp()
        self.repository['newsletter'] = zeit.cms.repository.folder.Folder()
        self.repository['newsletter']['taeglich'] = NewsletterCategory()
        transaction.commit()

    def test_metadata_of_category_is_editable(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/newsletter/taeglich'
               '/@@checkout')
        b.getControl('Optivo Mandant ID').value = '12345'
        b.getControl('Name of recipient list').value = 'foo'
        b.getControl('Subject').value = 'foo'
        b.getControl('Number of groups above middle ad').value = '3'
        b.getControl('Middle ad target URL').value = 'foo'
        b.getControl('Middle ad title').value = 'foo'
        b.getControl('Middle ad text').value = 'foo'
        b.getControl('Number of groups above this week\'s ad').value = '5'
        b.getControl('This week\'s ad target URL').value = 'foo'
        b.getControl('This week\'s ad title').value = 'foo'
        b.getControl('This week\'s ad text').value = 'foo'
        b.getControl('Bottom ad target URL').value = 'foo'
        b.getControl('Bottom ad title').value = 'foo'
        b.getControl('Bottom ad text').value = 'foo'
        b.getControl('Apply').click()
        b.getLink('Checkin').click()
        b.getLink('View metadata').click()
        self.assertEllipsis('...12345...', b.contents)
