from zeit.brightcove.update2 import import_video
from zeit.cms.interfaces import ICMSContent
import mock
import zeit.brightcove.testing
import zeit.cms.testing
import zeit.cms.workflow.interfaces


class ImportCMSVideoTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.brightcove.testing.ZCML_LAYER

    def create_video(self):
        bc = zeit.brightcove.convert2.Video()
        bc.data = {
            'id': 'myvid',
            'name': 'title',
            'created_at': '2017-05-15T08:24:55.916Z',
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
        bc.title = 'changed'
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        self.assertEqual('changed', video.title)

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

    def test_deleted_video_should_be_deleted_from_cms(self):
        bc = self.create_video()
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        deleted = zeit.brightcove.convert2.DeletedVideo(bc.id, video)
        import_video(deleted)
        self.assertEqual(
            None, ICMSContent('http://xml.zeit.de/video/2017-05/myvid', None))

    def test_deleted_video_should_be_retracted(self):
        bc = self.create_video()
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        deleted = zeit.brightcove.convert2.DeletedVideo(bc.id, video)
        with mock.patch('zeit.workflow.publish.Publish.retract') as retract:
            import_video(deleted)
            self.assertEqual(True, retract.called)
