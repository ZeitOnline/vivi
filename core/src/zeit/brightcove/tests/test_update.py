from datetime import datetime
from zeit.brightcove.update import import_video, import_playlist
from zeit.cms.interfaces import ICMSContent
import mock
import pytz
import transaction
import zeit.brightcove.testing
import zeit.cms.content.interfaces
import zeit.cms.testing
import zeit.cms.workflow.interfaces
import zeit.content.video.video


class ImportVideoTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.brightcove.testing.LAYER

    def create_video(self):
        bc = zeit.brightcove.convert.Video()
        bc.data = {
            'id': 'myvid',
            'name': 'title',
            'created_at': '2017-05-15T08:24:55.916Z',
            'updated_at': '2017-05-16T08:24:55.916Z',
            'state': 'ACTIVE',
            'custom_fields': {},
        }
        return bc

    def test_new_video_should_be_added_to_cms(self):
        self.assertEqual(
            None, ICMSContent('http://xml.zeit.de/video/2017-05/myvid', None))
        import_video(self.create_video())
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        self.assertEqual('title', video.title)
        info = zeit.cms.workflow.interfaces.IPublishInfo(video)
        self.assertEqual(True, info.published)

    def test_changed_video_should_be_written_to_cms(self):
        bc = self.create_video()
        import_video(bc)
        bc.data['name'] = 'changed'
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        self.assertEqual('changed', video.title)
        lsc = zeit.cms.content.interfaces.ISemanticChange(video)
        self.assertEqual(
            datetime(2017, 5, 16, 8, 24, 55, 916000, tzinfo=pytz.UTC),
            lsc.last_semantic_change)

    def test_should_publish_after_update(self):
        bc = self.create_video()
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        info = zeit.cms.workflow.interfaces.IPublishInfo(video)
        last_published = info.date_last_published
        import_video(bc)
        self.assertGreater(info.date_last_published, last_published)

    def test_should_publish_only_once(self):
        # Safetybelt against the "publish videos after checkin" feature
        bc = self.create_video()
        import_video(bc)  # Create CMS object
        with mock.patch('zeit.workflow.publish.Publish.publish') as publish:
            import_video(bc)
            self.assertEqual(1, publish.call_count)

    def test_ignored_video_should_not_be_added_to_cms(self):
        self.assertEqual(
            None, ICMSContent('http://xml.zeit.de/video/2017-05/myvid', None))
        bc = self.create_video()
        bc.data['custom_fields']['ignore_for_update'] = '1'
        import_video(bc)
        self.assertEqual(
            None, ICMSContent('http://xml.zeit.de/video/2017-05/myvid', None))

    def test_ignored_video_should_not_be_updated_in_cms(self):
        bc = self.create_video()
        import_video(bc)
        bc.data['name'] = 'changed'
        bc.data['custom_fields']['ignore_for_update'] = '1'
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        self.assertEqual('title', video.title)

    def test_inactive_video_should_be_retracted(self):
        bc = self.create_video()
        import_video(bc)
        bc.data['state'] = 'INACTIVE'
        with mock.patch('zeit.workflow.publish.Publish.retract') as retract:
            import_video(bc)
            self.assertEqual(True, retract.called)

    def test_inactive_video_should_be_imported_but_not_published(self):
        bc = self.create_video()
        bc.data['state'] = 'INACTIVE'
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        info = zeit.cms.workflow.interfaces.IPublishInfo(video)
        self.assertEqual(False, info.published)

    def test_changes_to_inactive_video_should_be_imported(self):
        bc = self.create_video()
        import_video(bc)
        bc.data['name'] = 'changed'
        bc.data['state'] = 'INACTIVE'
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        self.assertEqual('changed', video.title)
        info = zeit.cms.workflow.interfaces.IPublishInfo(video)
        self.assertEqual(False, info.published)

    def test_deleted_video_should_be_deleted_from_cms(self):
        bc = self.create_video()
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        deleted = zeit.brightcove.convert.DeletedVideo(bc.id, video)
        import_video(deleted)
        self.assertEqual(
            None, ICMSContent('http://xml.zeit.de/video/2017-05/myvid', None))

    def test_deleted_video_should_be_retracted(self):
        bc = self.create_video()
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        deleted = zeit.brightcove.convert.DeletedVideo(bc.id, video)
        with mock.patch('zeit.workflow.publish.Publish.retract') as retract:
            import_video(deleted)
            self.assertEqual(True, retract.called)


class ImportPlaylistTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.brightcove.testing.LAYER

    def create_playlist(self):
        bc = zeit.brightcove.convert.Playlist()
        bc.data = {
            'id': 'mypls',
            'name': 'title',
            'updated_at': '2017-05-15T08:24:55.916Z',
        }
        return bc

    def test_new_playlist_should_be_added_to_cms(self):
        self.assertEqual(
            None, ICMSContent('http://xml.zeit.de/video/playlist/mypls', None))
        import_playlist(self.create_playlist())
        playlist = ICMSContent('http://xml.zeit.de/video/playlist/mypls')
        self.assertEqual('title', playlist.title)
        info = zeit.cms.workflow.interfaces.IPublishInfo(playlist)
        self.assertEqual(True, info.published)

    def test_changed_playlist_should_be_written_to_cms_if_newer(self):
        bc = self.create_playlist()
        import_playlist(bc)
        playlist = ICMSContent('http://xml.zeit.de/video/playlist/mypls')
        self.assertEqual('title', playlist.title)
        info = zeit.cms.workflow.interfaces.IPublishInfo(playlist)
        last_published = info.date_last_published

        bc.data['name'] = 'changed'
        import_playlist(bc)
        playlist = ICMSContent('http://xml.zeit.de/video/playlist/mypls')
        self.assertEqual('title', playlist.title)

        bc.data['updated_at'] = '2017-05-16T08:24:55.916Z'
        import_playlist(bc)

        playlist = ICMSContent('http://xml.zeit.de/video/playlist/mypls')
        self.assertEqual('changed', playlist.title)
        lsc = zeit.cms.content.interfaces.ISemanticChange(playlist)
        self.assertEqual(
            datetime(2017, 5, 16, 8, 24, 55, 916000, tzinfo=pytz.UTC),
            lsc.last_semantic_change)
        self.assertGreater(info.date_last_published, last_published)

    def test_unknown_playlist_should_be_deleted(self):
        bc = self.create_playlist()
        import_playlist(bc)
        other = self.create_playlist()
        other.data['id'] = 'other'
        import_playlist(other)

        import_playlist.delete_except([other])
        self.assertEqual(
            None, ICMSContent('http://xml.zeit.de/video/playlist/mypls', None))
        self.assertNotEqual(
            None, ICMSContent('http://xml.zeit.de/video/playlist/other', None))


class ExportTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.brightcove.testing.LAYER

    def setUp(self):
        super(ExportTest, self).setUp()
        self.repository['myvid'] = zeit.content.video.video.Video()
        self.request_patch = mock.patch(
            'zeit.brightcove.connection.CMSAPI._request')
        self.request = self.request_patch.start()

    def tearDown(self):
        self.request_patch.stop()
        super(ExportTest, self).tearDown()

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
        video = zeit.brightcove.convert.Video()
        zeit.brightcove.session.get().update_video(video)
        transaction.commit()
        self.assertEqual(1, self.request.call_count)
        # Changes are not written again
        transaction.commit()
        self.assertEqual(1, self.request.call_count)

    def test_changes_are_not_written_on_abort(self):
        video = zeit.brightcove.convert.Video()
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

        self.assertGreater(info.date_last_published, last_published)
