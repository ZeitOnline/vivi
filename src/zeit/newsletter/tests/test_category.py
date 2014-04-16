# Copyright (c) 2011-2014 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.newsletter.category import NewsletterCategory
from zeit.newsletter.newsletter import Newsletter
from zeit.cms.testcontenttype.testcontenttype import TestContentType
import datetime
import mock
import pytz
import zeit.cms.repository.folder
import zeit.newsletter.testing


class CreateNewsletterTest(zeit.newsletter.testing.TestCase):

    def setUp(self):
        super(CreateNewsletterTest, self).setUp()
        self.category = NewsletterCategory()
        self.category.subject = 'nosubject'
        self.repository['mynl'] = self.category

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

    def test_last_creation_time_is_remembered(self):
        from datetime import datetime
        dt = mock.Mock()
        dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        timestamp1 = datetime(2011, 6, 29, 10, 0, tzinfo=pytz.UTC)
        timestamp2 = datetime(2011, 6, 29, 15, 0, tzinfo=pytz.UTC)

        with mock.patch('datetime.datetime', dt):
            self.category._get_content_newer_than = mock.Mock()

            dt.now.return_value = timestamp1
            self.category.create()
            self.category._get_content_newer_than.assert_called_with(None)

            dt.now.return_value = timestamp2
            self.category.create()
            self.category._get_content_newer_than.assert_called_with(
                timestamp1)

    def test_smoke_query_for_newer_content(self):
        # this is just a smoke test (against syntax errors and such),
        # since the mock connector doesn't implement search
        ANY = datetime.datetime(2001, 6, 29, 10, 0)
        self.assertEqual(
            3, len(list(self.category._get_content_newer_than(ANY))))

    def test_query_with_none_returns_empty_list(self):
        # XXX is this what we want for the first-ever newsletter created?
        self.assertEqual(
            [], list(self.category._get_content_newer_than(None)))

    def test_get_content_newer_than_should_return_objects(self):
        from zeit.cms.interfaces import ICMSContent
        ANY = datetime.datetime(2001, 6, 29, 10, 0)
        result = list(self.category._get_content_newer_than(ANY))
        for obj in result:
            self.assertTrue(ICMSContent.providedBy(obj), obj)

    def test_subject_interpolates_date(self):
        from zeit.cms.checkout.helper import checked_out
        with checked_out(self.repository['mynl']) as category:
            category.subject = 'foo {today}'

        timestamp = datetime.datetime(2001, 6, 29, 10, 0, tzinfo=pytz.UTC)
        with mock.patch('datetime.datetime') as dt:
            self.category._get_content_newer_than = mock.Mock()
            dt.now.return_value = timestamp
            newsletter = self.repository['mynl'].create()

        self.assertEqual('foo 29.06.2001', newsletter.subject)


class DailyNewsletterBuilderTest(zeit.newsletter.testing.TestCase):

    def setUp(self):
        super(DailyNewsletterBuilderTest, self).setUp()
        self.category = NewsletterCategory()
        self.category.subject = 'nosubject'
        self.repository['mynl'] = self.category
        self.newsletter = Newsletter()
        self.builder = zeit.newsletter.category.DailyNewsletterBuilder(
            self.category, self.newsletter)

    def create_content(self, name, ressort):
        content = TestContentType()
        content.ressort = ressort
        self.repository[name] = content
        return self.repository[name]

    def test_groups_content_according_to_ressort(self):
        c1 = self.create_content('c1', u'Politik')
        c2 = self.create_content('c2', u'Wirtschaft')
        c3 = self.create_content('c3', u'Politik')
        self.builder([c1, c2, c3])

        body = self.newsletter['newsletter_body']
        self.assertEqual(3, len(body))
        group1 = body[body.keys()[0]]
        group2 = body[body.keys()[1]]
        self.assertEqual(u'Politik', group1.title)
        self.assertEqual(u'Wirtschaft', group2.title)

        self.assertEqual([c1, c3], [x.reference for x in group1.values()])
        self.assertEqual([c2], [x.reference for x in group2.values()])

    def test_group_should_work_if_content_not_adaptable_to_metadata(self):
        c1 = self.create_content('c1', u'Politik')
        try:
            self.builder([mock.Mock(), c1])
        except TypeError, e:
            if 'Could not adapt' == e.args[0]:
                self.fail('Adaptation should not fail. Raised: %s' % e)
            raise e
        body = self.newsletter['newsletter_body']
        group1 = body[body.keys()[0]]
        self.assertEqual(u'Politik', group1.title)

    def test_video_group_should_be_appended(self):
        self.builder(())
        body = self.newsletter['newsletter_body']
        self.assertEqual(1, len(body))
        self.assertEqual('Videos', body.values()[0].title)

    def test_should_not_break_if_playlist_id_resolves_to_something_else(self):
        self.category.video_playlist = self.category.uniqueId
        self.builder(())
        body = self.newsletter['newsletter_body']
        self.assertEqual(1, len(body))
        self.assertEqual('Videos', body.values()[0].title)

    def test_should_populate_video_group_from_playlist(self):
        playlist = zeit.content.video.playlist.Playlist()
        video1 = zeit.content.video.video.Video()
        video2 = zeit.content.video.video.Video()
        video1.title = 'Video 1'
        self.repository['video1'] = video1
        video2.title = 'Video 2'
        self.repository['video2'] = video2
        playlist.videos = (video1, video2)
        self.repository['playlist'] = playlist

        self.category.video_playlist = playlist.uniqueId
        self.builder(())
        body = self.newsletter['newsletter_body']
        video_group = body.values()[-1]
        self.assertEqual(2, len(video_group))
        self.assertEqual('Video 1', video_group.values()[0].reference.title)
        self.assertEqual('Video 2', video_group.values()[1].reference.title)
