# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.newsletter.category import NewsletterCategory
import datetime
import zeit.cms.repository.folder
import zeit.newsletter.testing


class CreateNewsletterTest(zeit.newsletter.testing.TestCase):

    def setUp(self):
        super(CreateNewsletterTest, self).setUp()
        self.repository['mynl'] = NewsletterCategory()
        self.category = self.repository['mynl']

    def test_should_assemble_folder_name_from_year_and_month(self):
        folder = self.category._find_or_create_folder(
            datetime.date(2011, 6, 29))
        self.assertEqual('2011-06', folder.__name__)

    def test_should_reuse_existing_folder(self):
        self.category['2011-06'] = zeit.cms.repository.folder.Folder()
        folder = self.category['2011-06']
        created = self.category._find_or_create_folder(
            datetime.date(2011, 6, 29))
        self.assertIs(folder, created)

    def test_choose_name_should_use_day(self):
        self.category['2011-06'] = zeit.cms.repository.folder.Folder()
        folder = self.category['2011-06']
        name = self.category._choose_name(folder, datetime.date(2011, 6, 29))
        self.assertEqual('29-1', name)

    def test_choose_name_should_increment_suffix(self):
        self.category['2011-06'] = zeit.cms.repository.folder.Folder()
        folder = self.category['2011-06']
        folder['29-1'] = zeit.cms.repository.folder.Folder()
        name = self.category._choose_name(folder, datetime.date(2011, 6, 29))
        self.assertEqual('29-2', name)
