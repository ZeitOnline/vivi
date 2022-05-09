from unittest import mock
from zeit.cms.checkout.helper import checked_out
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.newsletter.category import NewsletterCategory
from zeit.newsletter.interfaces import INewsletterCategory
from zeit.newsletter.newsletter import Newsletter
import datetime
import pytz
import zeit.cms.repository.folder
import zeit.newsletter.testing
import zope.dublincore.interfaces
import zope.schema


class InvariantsTest(zeit.newsletter.testing.TestCase):

    def test_middle_ad_above_thisweeks_ad_validates(self):
        category = NewsletterCategory()
        category.ad_middle_groups_above = 2
        category.ad_thisweeks_groups_above = 3
        try:
            INewsletterCategory.validateInvariants(category)
        except zope.schema.ValidationError as e:
            raise AssertionError(e)

    def test_middle_ad_same_place_as_thisweeks_ad_raises(self):
        category = NewsletterCategory()
        category.ad_middle_groups_above = 2
        category.ad_thisweeks_groups_above = 2
        self.assertRaises(
            zope.schema.ValidationError,
            lambda: INewsletterCategory.validateInvariants(category))

    def test_middle_ad_below_thisweeks_ad_raises(self):
        category = NewsletterCategory()
        category.ad_middle_groups_above = 3
        category.ad_thisweeks_groups_above = 2
        self.assertRaises(
            zope.schema.ValidationError,
            lambda: INewsletterCategory.validateInvariants(category))


class CreateNewsletterTest(zeit.newsletter.testing.TestCase):

    def setUp(self):
        super().setUp()
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

    # XXX re VIV-510: In addition to the following test, we'd need one that
    # asserts that creation times do get stored when a newsletter was
    # successfully published. While this is true for trying it out in a
    # running instance, something in the test setup used to break the identity
    # of the category object between test code and Newsletter.send(). Left
    # this test as an exercise to be completed after an urgent feature release.

    def test_last_creation_time_is_not_remembered_while_unpublished(self):
        from datetime import datetime
        dt = mock.Mock()
        dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        timestamp1 = datetime(2011, 6, 29, 10, 0, tzinfo=pytz.UTC)
        timestamp2 = datetime(2011, 6, 29, 15, 0, tzinfo=pytz.UTC)

        with mock.patch('datetime.datetime', dt):
            self.category._get_content_newer_than = mock.Mock()
            self.category._get_content_newer_than.return_value = []

            dt.now.return_value = timestamp1
            self.category.create()
            self.category._get_content_newer_than.assert_called_with(None)

            dt.now.return_value = timestamp2
            self.category.create()
            self.category._get_content_newer_than.assert_called_with(
                None)

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

    def test_smoke_test_for_populated_newletter_body(self):
        # this is just a smoke test to make sure things are wired up,
        # since the mock connector doesn't implement search
        with mock.patch('zeit.newsletter.category.Builder.__call__') as build:
            self.repository['mynl'].create()
            build.assert_called()


class BuilderTest(zeit.newsletter.testing.TestCase):

    NON_RESSORT_ELEMENTS = 4  # video group, ads: middle, this week's, bottom
    VIDEO_GROUP_POSITION = -2
    MIDDLE_AD_GROUPS_ABOVE = 1
    THISWEEKS_AD_GROUPS_ABOVE = 2
    BOTTOM_AD_POSITION = -1

    def setUp(self):
        super().setUp()
        self.category = NewsletterCategory()
        self.category.ressorts = ('Politik', 'Wirtschaft')
        self.category.subject = 'nosubject'
        self.category.ad_middle_groups_above = self.MIDDLE_AD_GROUPS_ABOVE
        self.category.ad_thisweeks_groups_above = \
            self.THISWEEKS_AD_GROUPS_ABOVE
        self.repository['mynl'] = self.category
        self.category = self.repository['mynl']
        self.newsletter = self.repository['mynl']['newsletter'] = Newsletter()
        self.builder = zeit.newsletter.category.Builder(
            self.repository['mynl'], self.newsletter)

    def create_content(self, name, ressort):
        content = ExampleContentType()
        content.ressort = ressort
        self.repository[name] = content
        return self.repository[name]

    def test_groups_content_according_to_ressort(self):
        c1 = self.create_content('c1', 'Politik')
        c2 = self.create_content('c2', 'Wirtschaft')
        c3 = self.create_content('c3', 'Politik')
        c4 = self.create_content('c4', 'Kultur')
        self.builder([c1, c2, c3, c4])

        body = self.newsletter['newsletter_body']
        self.assertEqual(2 + self.NON_RESSORT_ELEMENTS, len(body))
        groups = [el for el in body.values() if el.type == 'group']
        group1, group2 = groups[:2]
        self.assertEqual('Politik', group1.title)
        self.assertEqual('Wirtschaft', group2.title)

        self.assertEqual([c1, c3], [x.reference for x in group1.values()])
        self.assertEqual([c2], [x.reference for x in group2.values()])

    def test_configured_ressorts_are_contained_even_if_empty(self):
        c1 = self.create_content('c1', 'Politik')
        c2 = self.create_content('c2', 'Kultur')
        c3 = self.create_content('c3', 'Politik')
        self.builder([c1, c2, c3])

        body = self.newsletter['newsletter_body']
        self.assertEqual(2 + self.NON_RESSORT_ELEMENTS, len(body))
        groups = [el for el in body.values() if el.type == 'group']
        group1, group2 = groups[:2]
        self.assertEqual('Politik', group1.title)
        self.assertEqual('Wirtschaft', group2.title)

        self.assertEqual([], group2.values())

    def test_group_should_work_if_content_not_adaptable_to_metadata(self):
        c1 = self.create_content('c1', 'Politik')
        try:
            self.builder([mock.Mock(), c1])
        except TypeError as e:
            if 'Could not adapt' == e.args[0]:
                self.fail('Adaptation should not fail. Raised: %s' % e)
            raise e
        body = self.newsletter['newsletter_body']
        group1 = body[body.keys()[0]]
        self.assertEqual('Politik', group1.title)

    def test_video_group_should_be_appended_even_if_empty(self):
        self.builder(())
        body = self.newsletter['newsletter_body']
        self.assertNotEqual(0, len(body))
        video_group = body.values()[self.VIDEO_GROUP_POSITION]
        self.assertEqual('Video', video_group.title)
        self.assertEqual(0, len(video_group))

    def test_should_not_break_if_playlist_id_resolves_to_something_else(self):
        with checked_out(self.category) as co:
            co.video_playlist = self.category.uniqueId
        self.builder(())
        body = self.newsletter['newsletter_body']
        self.assertNotEqual(0, len(body))
        video_group = body.values()[self.VIDEO_GROUP_POSITION]
        self.assertEqual('Video', video_group.title)
        self.assertEqual(0, len(video_group))

    def test_should_populate_video_group_from_playlist(self):
        created = datetime.datetime(2014, 9, 22, 8, 0, tzinfo=pytz.UTC)

        video1 = zeit.content.video.video.Video()
        video2 = zeit.content.video.video.Video()
        video1.title = 'Video 1'
        self.repository['video1'] = video1
        video1 = self.repository['video1']
        with checked_out(video1) as co:
            zope.dublincore.interfaces.IDCTimes(co).created = created
        video2.title = 'Video 2'
        self.repository['video2'] = video2
        video2 = self.repository['video2']
        with checked_out(video2) as co:
            zope.dublincore.interfaces.IDCTimes(co).created = created

        playlist = zeit.content.video.playlist.Playlist()
        playlist.videos = (video1, video2)
        self.repository['playlist'] = playlist

        with checked_out(self.category) as co:
            co.video_playlist = playlist.uniqueId
        self.category.last_created = created - datetime.timedelta(1)

        self.builder(())
        body = self.newsletter['newsletter_body']
        video_group = body.values()[self.VIDEO_GROUP_POSITION]
        self.assertEqual(2, len(video_group))
        self.assertEqual('Video 1', video_group.values()[0].reference.title)
        self.assertEqual('Video 2', video_group.values()[1].reference.title)

    def test_should_populate_video_group_using_last_created_date(self):
        video1 = zeit.content.video.video.Video()
        video2 = zeit.content.video.video.Video()
        video3 = zeit.content.video.video.Video()
        video1.title = 'Video 1'
        video2.title = 'Video 2'
        video3.title = 'Video 3'
        self.repository['video1'] = video1
        self.repository['video2'] = video2
        self.repository['video3'] = video3
        video1 = self.repository['video1']
        video2 = self.repository['video2']
        video3 = self.repository['video3']

        with checked_out(video1) as co:
            co.title = 'Video 1'
            # Keep created date value None to make sure this can be handled.
        with checked_out(video2) as co:
            co.title = 'Video 2'
            zope.dublincore.interfaces.IDCTimes(co).created = \
                datetime.datetime(2014, 9, 22, 8, 0, tzinfo=pytz.UTC)
        with checked_out(video3) as co:
            co.title = 'Video 3'
            zope.dublincore.interfaces.IDCTimes(co).created = \
                datetime.datetime(2014, 9, 23, 8, 0, tzinfo=pytz.UTC)

        playlist = zeit.content.video.playlist.Playlist()
        playlist.videos = (video1, video2, video3)
        self.repository['playlist'] = playlist

        with checked_out(self.category) as co:
            co.video_playlist = playlist.uniqueId
        self.category.last_created = datetime.datetime(
            2014, 9, 22, 18, 0, tzinfo=pytz.UTC)
        self.builder(())

        body = self.newsletter['newsletter_body']
        video_group = body.values()[self.VIDEO_GROUP_POSITION]
        self.assertEqual(1, len(video_group))
        self.assertEqual('Video 3', video_group.values()[0].reference.title)

    def test_middle_advertisement_should_be_inserted(self):
        with checked_out(self.repository['mynl']) as co:
            co.ad_middle_title = 'Some ad'
        c1 = self.create_content('c1', 'Politik')
        c2 = self.create_content('c2', 'Wirtschaft')
        self.builder((c1, c2))
        body = self.newsletter['newsletter_body']
        advertisement = body[self.MIDDLE_AD_GROUPS_ABOVE]
        self.assertEqual('advertisement-middle', advertisement.type)
        self.assertEqual('Some ad', advertisement.title)

    def test_thisweeks_advertisement_should_be_inserted(self):
        with checked_out(self.repository['mynl']) as co:
            co.ad_thisweeks_title = 'Some ad'
        c1 = self.create_content('c1', 'Politik')
        c2 = self.create_content('c2', 'Wirtschaft')
        c3 = self.create_content('c3', 'Kultur')
        self.builder((c1, c2, c3))
        body = self.newsletter['newsletter_body']
        advertisement = body[self.THISWEEKS_AD_GROUPS_ABOVE + 1]
        self.assertEqual('advertisement-thisweeks', advertisement.type)
        self.assertEqual('Some ad', advertisement.title)

    def test_thisweeks_advert_should_be_omitted_on_unchecked_weekday(self):
        weekday = datetime.date.today().weekday()
        with checked_out(self.repository['mynl']) as co:
            co.ad_thisweeks_title = 'Some ad'
            setattr(co, 'ad_thisweeks_on_%d' % weekday, False)
        self.builder(())
        body = self.newsletter['newsletter_body']
        self.assertFalse(
            any(ad.type == 'advertisement-thisweeks' for ad in body.values()))

    def test_bottom_advertisement_should_be_appended(self):
        with checked_out(self.repository['mynl']) as co:
            co.ad_bottom_title = 'Some ad'
        self.builder(())
        body = self.newsletter['newsletter_body']
        advertisement = body[self.BOTTOM_AD_POSITION]
        self.assertEqual('advertisement-bottom', advertisement.type)
        self.assertEqual('Some ad', advertisement.title)
