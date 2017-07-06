from zeit.brightcove.convert2 import Video as BCVideo
from zeit.content.video.video import Video as CMSVideo
import mock
import transaction
import zeit.brightcove.testing
import zeit.cms.testing


class VideoTest(zeit.cms.testing.FunctionalTestCase,
                zeit.cms.tagging.testing.TaggingHelper):

    layer = zeit.brightcove.testing.ZCML_LAYER

    def test_converts_cms_fields_to_bc_names(self):
        cms = CMSVideo()
        cms.title = u'title'
        cms.teaserText = u'teaser'
        bc = BCVideo.from_cms(cms)
        self.assertEqual('title', bc.data['name'])
        self.assertEqual('teaser', bc.data['description'])

    def test_readonly_fields_are_removed_for_writing(self):
        bc = BCVideo()
        bc.data['id'] = 'foo'
        self.assertNotIn('id', bc.write_data)

    def test_looks_up_type_conversion_by_field(self):
        cms = CMSVideo()
        cms.commentsAllowed = True
        bc = BCVideo.from_cms(cms)
        self.assertEqual('1', bc.data['custom_fields']['allow_comments'])

    def test_converts_authors(self):
        from zeit.content.author.author import Author
        self.repository['a1'] = Author()
        self.repository['a2'] = Author()

        cms = CMSVideo()
        cms.authorships = (
            cms.authorships.create(self.repository['a1']),
            cms.authorships.create(self.repository['a2'])
        )
        bc = BCVideo.from_cms(cms)
        self.assertEqual(
            'http://xml.zeit.de/a1 http://xml.zeit.de/a2',
            bc.data['custom_fields']['authors'])

    def test_converts_keywords(self):
        cms = CMSVideo()
        self.setup_tags('staatsanwaltschaft', 'parlament')
        bc = BCVideo.from_cms(cms)
        self.assertEqual(
            'staatsanwaltschaft;parlament',
            bc.data['custom_fields']['cmskeywords'])

    def test_converts_product(self):
        cms = CMSVideo()
        cms.product = zeit.cms.content.sources.PRODUCT_SOURCE(None).find(
            'TEST')
        bc = BCVideo.from_cms(cms)
        self.assertEqual('TEST', bc.data['custom_fields']['produkt-id'])

    def test_converts_serie(self):
        cms = CMSVideo()
        cms.serie = zeit.content.video.interfaces.IVideo['serie'].source(
            None).find('erde/umwelt')
        bc = BCVideo.from_cms(cms)
        self.assertEqual('erde/umwelt', bc.data['custom_fields']['serie'])

    def test_converts_related(self):
        cms = CMSVideo()
        related = zeit.cms.related.interfaces.IRelatedContent(cms)
        related.related = (
            zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/online/2007/01/eta-zapatero'),)
        bc = BCVideo.from_cms(cms)
        self.assertEqual(
            'http://xml.zeit.de/online/2007/01/eta-zapatero',
            bc.data['custom_fields']['ref_link1'])


class SaveTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.brightcove.testing.ZCML_LAYER

    def setUp(self):
        super(SaveTest, self).setUp()
        self.repository['myvid'] = CMSVideo()
        self.request_patch = mock.patch(
            'zeit.brightcove.connection2.CMSAPI._request')
        self.request = self.request_patch.start()

    def tearDown(self):
        self.request_patch.stop()
        super(SaveTest, self).tearDown()

    def test_video_changes_are_written_to_brightcove_on_checkin(self):
        with zeit.cms.checkout.helper.checked_out(
                self.repository['myvid'], semantic_change=True) as co:
            co.title = u'local change'
        transaction.commit()
        self.assertEqual(1, self.request.call_count)
        self.assertEqual(
            'local change', self.request.call_args[1]['body']['name'])

    def test_changes_are_not_written_during_publish(self):
        zeit.cms.workflow.interfaces.IPublish(
            self.repository['myvid']).publish(async=False)
        self.assertEqual(False, self.request.called)

    def test_changes_are_written_on_commit(self):
        video = BCVideo()
        zeit.brightcove.session.get().update_video(video)
        transaction.commit()
        self.assertEqual(1, self.request.call_count)
        # Changes are not written again
        transaction.commit()
        self.assertEqual(1, self.request.call_count)

    def test_changes_are_not_written_on_abort(self):
        video = BCVideo()
        zeit.brightcove.session.get().update_video(video)
        transaction.abort()
        self.assertEqual(0, self.request.call_count)

    def test_video_is_published_on_checkin(self):
        video = self.repository['myvid']
        zeit.cms.workflow.interfaces.IPublish(video).publish(async=False)
        info = zeit.cms.workflow.interfaces.IPublishInfo(video)
        last_published = info.date_last_published

        with zeit.cms.checkout.helper.checked_out(video):
            pass
        transaction.commit()
        zeit.workflow.testing.run_publish()

        self.assertGreater(info.date_last_published, last_published)

    def test_playlist_is_published_on_checkin(self):
        self.repository['playlist'] = zeit.content.video.playlist.Playlist()
        playlist = self.repository['playlist']
        zeit.cms.workflow.interfaces.IPublish(playlist).publish(async=False)
        info = zeit.cms.workflow.interfaces.IPublishInfo(playlist)
        last_published = info.date_last_published

        with zeit.cms.checkout.helper.checked_out(playlist):
            pass
        transaction.commit()
        zeit.workflow.testing.run_publish()

        self.assertGreater(info.date_last_published, last_published)
