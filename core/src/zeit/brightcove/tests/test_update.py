from os import path
from unittest import mock
import importlib.resources
import shutil

from pendulum import datetime
import transaction
import zope.security.management

from zeit.brightcove.update import import_video
from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.interfaces import ICMSContent
import zeit.brightcove.testing
import zeit.cms.content.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.image.testing
import zeit.content.video.video


def create_video():
    bc = zeit.brightcove.convert.Video()
    bc.data = {
        'id': 'myvid',
        'name': 'title',
        'created_at': '2017-05-15T08:24:55.916Z',
        'updated_at': '2017-05-16T08:24:55.916Z',
        'state': 'ACTIVE',
        'custom_fields': {},
        'images': {'poster': {'src': 'nosuchhost'}},
    }
    return bc


class ImportVideoTest(zeit.brightcove.testing.FunctionalTestCase):
    def test_new_video_should_be_added_to_cms(self):
        self.assertEqual(None, ICMSContent('http://xml.zeit.de/video/2017-05/myvid', None))
        import_video(create_video())
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        self.assertEqual('title', video.title)
        info = zeit.cms.workflow.interfaces.IPublishInfo(video)
        self.assertEqual(True, info.published)

    def test_new_video_should_create_still_image_group(self):
        import_video(create_video())
        assert self.repository['video']['2017-05']['myvid'].video_still is None
        assert self.repository['video']['2017-05']['myvid-still'] is not None

    def test_should_not_create_still_image_group_for_missing_src(self):
        video = create_video()
        del video.data['images']
        import_video(video)
        assert self.repository['video']['2017-05']['myvid'].video_still is None
        assert self.repository['video']['2017-05'].get('myvid-still') is None

    def test_changed_video_should_be_written_to_cms(self):
        bc = create_video()
        import_video(bc)
        bc.data['name'] = 'changed'
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        self.assertEqual('changed', video.title)
        lsc = zeit.cms.content.interfaces.ISemanticChange(video)
        self.assertEqual(datetime(2017, 5, 16, 8, 24, 55, 916000), lsc.last_semantic_change)

    def test_should_publish_after_update(self):
        bc = create_video()
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        info = zeit.cms.workflow.interfaces.IPublishInfo(video)
        last_published = info.date_last_published
        import_video(bc)
        self.assertGreater(info.date_last_published, last_published)

    def test_should_publish_only_once(self):
        # Safetybelt against the "publish videos after checkin" feature
        bc = create_video()
        import_video(bc)  # Create CMS object
        publish = mock.Mock()
        zope.component.getGlobalSiteManager().registerHandler(
            publish, (zeit.cms.workflow.interfaces.IPublishedEvent,)
        )
        import_video(bc)
        self.assertEqual(2, publish.call_count)  # video + still

    def test_should_ignore_publish_for_already_locked_object(self):
        bc = create_video()
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        info = zeit.cms.workflow.interfaces.IPublishInfo(video)
        last_published = info.date_last_published

        zope.security.management.endInteraction()
        with zeit.cms.testing.interaction('zope.producer'):
            zeit.cms.checkout.interfaces.ICheckoutManager(video).checkout()
        zeit.cms.testing.create_interaction('zope.user')

        import_video(bc)
        self.assertEqual(info.date_last_published, last_published)

    def test_ignored_video_should_not_be_added_to_cms(self):
        self.assertEqual(None, ICMSContent('http://xml.zeit.de/video/2017-05/myvid', None))
        bc = create_video()
        bc.data['custom_fields']['ignore_for_update'] = '1'
        import_video(bc)
        self.assertEqual(None, ICMSContent('http://xml.zeit.de/video/2017-05/myvid', None))

    def test_ignored_video_should_not_be_updated_in_cms(self):
        bc = create_video()
        import_video(bc)
        bc.data['name'] = 'changed'
        bc.data['custom_fields']['ignore_for_update'] = '1'
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        self.assertEqual('title', video.title)

    def test_inactive_video_should_be_imported_but_not_published(self):
        bc = create_video()
        bc.data['state'] = 'INACTIVE'
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        info = zeit.cms.workflow.interfaces.IPublishInfo(video)
        self.assertEqual(False, info.published)

    def test_changes_to_inactive_video_should_be_imported(self):
        bc = create_video()
        import_video(bc)
        bc.data['name'] = 'changed'
        bc.data['state'] = 'INACTIVE'
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        self.assertEqual('changed', video.title)
        info = zeit.cms.workflow.interfaces.IPublishInfo(video)
        self.assertEqual(False, info.published)

    def test_inactive_video_should_be_retracted(self):
        bc = create_video()
        import_video(bc)
        bc.data['state'] = 'INACTIVE'
        retract = mock.Mock()
        zope.component.getGlobalSiteManager().registerHandler(
            retract, (zeit.cms.workflow.interfaces.IRetractedEvent,)
        )
        import_video(bc)
        self.assertEqual(True, retract.called)

    def test_deleted_video_should_be_retracted(self):
        bc = create_video()
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        deleted = zeit.brightcove.convert.DeletedVideo(bc.id, video)
        retract = mock.Mock()
        zope.component.getGlobalSiteManager().registerHandler(
            retract, (zeit.cms.workflow.interfaces.IRetractedEvent,)
        )
        import_video(deleted)
        self.assertEqual(True, retract.called)

    def test_images_of_retracted_video_should_be_retracted(self):
        import_video(create_video())
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        still = ICMSContent('http://xml.zeit.de/video/2017-05/myvid-still')
        info_video = zeit.cms.workflow.interfaces.IPublishInfo(video)
        info_still = zeit.cms.workflow.interfaces.IPublishInfo(still)
        self.assertEqual(True, info_video.published)
        self.assertEqual(True, info_still.published)
        zeit.cms.workflow.interfaces.IPublish(self.repository['video']['2017-05']['myvid']).retract(
            background=False
        )
        self.assertEqual(False, info_video.published)
        self.assertEqual(False, info_still.published)

    def test_deleted_video_and_images_should_be_deleted_from_cms(self):
        bc = create_video()
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid', None)
        still = ICMSContent('http://xml.zeit.de/video/2017-05/myvid-still/', None)
        assert video is not None
        assert still is not None
        deleted = zeit.brightcove.convert.DeletedVideo(bc.id, video)
        import_video(deleted)
        # XXX manual transaction.commit() to avoid running into a vivi bug
        transaction.commit()
        self.assertEqual(None, ICMSContent('http://xml.zeit.de/video/2017-05/myvid', None))
        self.assertEqual(None, ICMSContent('http://xml.zeit.de/video/2017-05/myvid-still/', None))

    def test_images_of_deleted_video_should_be_retracted(self):
        bc = create_video()
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        still = ICMSContent('http://xml.zeit.de/video/2017-05/myvid-still')
        deleted = zeit.brightcove.convert.DeletedVideo(bc.id, video)
        import_video(deleted)
        info_still = zeit.cms.workflow.interfaces.IPublishInfo(still)
        self.assertEqual(False, info_still.published)

    def test_vanished_video_should_be_ignored(self):
        bc = create_video()
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        del video.__parent__[video.__name__]
        deleted = zeit.brightcove.convert.DeletedVideo(bc.id, None)
        with self.assertNothingRaised():
            import_video(deleted)

    def test_new_video_should_have_authorship(self):
        author = zeit.content.author.author.Author()
        author.firstname = 'William'
        author.lastname = 'Shakespeare'
        self.repository['author'] = author
        bc = create_video()
        bc.data['custom_fields']['authors'] = 'http://xml.zeit.de/author'
        import_video(bc)
        video = ICMSContent('http://xml.zeit.de/video/2017-05/myvid')
        self.assertEqual(self.repository['author'], video.authorships[0].target)


class TestDownloadTeasers(zeit.brightcove.testing.StaticBrowserTestCase):
    def setUp(self):
        super().setUp()
        image_dir = importlib.resources.files('zeit.content.image.browser') / 'testdata'
        shutil.copytree(image_dir, path.join(self.layer['documentroot'], 'testdata'))

    def test_download_teaser_image__still_success(self):
        src = 'http://{0.layer[http_address]}/testdata/opernball.jpg'.format(self)
        bc = create_video()
        bc.data['images']['poster']['src'] = src
        import_video(bc)
        # importing the video has created an image group "next to it" for its still image
        video = self.repository['video']['2017-05']['myvid']
        img = zeit.content.image.interfaces.IImages(video)
        assert img.image == self.repository['video']['2017-05']['myvid-still']
        self.assertEqual(
            True,
            zeit.cms.workflow.interfaces.IPublishInfo(
                ICMSContent('http://xml.zeit.de/video/2017-05/myvid-still')
            ).published,
        )

    def test_download_teaser_for_locked_image_ignored(self):
        with mock.patch('zeit.content.image.imagegroup.ImageGroup.from_image') as patched:
            patched.side_effect = zope.app.locking.interfaces.LockingError()
            assert (
                zeit.brightcove.update.download_teaser_image(
                    self.repository,
                    {'id': 'foo', 'images': {'thumbnail': {'src': 'foo'}}},
                    'thumbnail',
                )
                is None
            )

    def test_update_teaser_image_still_success(self):
        src = 'http://{0.layer[http_address]}/testdata/opernball.jpg'.format(self)
        bc = create_video()
        bc.data['images']['poster']['src'] = src
        imported = import_video(bc)
        img = zeit.content.image.interfaces.IImages(imported.cmsobj)
        assert img.image.master_image == 'opernball.jpg'
        new_src = 'http://{0.layer[http_address]}/testdata/obama-clinton-120x120.jpg'.format(self)
        bc.data['images']['poster']['src'] = new_src
        # importing it again triggers update:
        reimported = import_video(bc)
        img = zeit.content.image.interfaces.IImages(reimported.cmsobj)
        assert img.image.master_image == 'obama-clinton-120x120.jpg'

    def test_update_teaser_image_preserves_override(self):
        from zeit.content.image.testing import create_image_group_with_master_image

        src = 'http://{0.layer[http_address]}/testdata/opernball.jpg'.format(self)
        # video is created via BC import
        bc = create_video()
        bc.data['images']['poster']['src'] = src
        import_video(bc)
        # editor replaces automatically created video still with custom imagegroup
        self.repository['foo-video_still'] = create_image_group_with_master_image()
        video = self.repository['video']['2017-05']['myvid']
        img = zeit.content.image.interfaces.IImages(video)
        img.image = self.repository['foo-video_still']
        img = zeit.content.image.interfaces.IImages(video)
        assert img.image.master_image == 'master-image.jpg'
        # now an update from brightcove still updates the automatically created image group:
        new_src = 'http://{0.layer[http_address]}/testdata/obama-clinton-120x120.jpg'.format(self)
        bc.data['images']['poster']['src'] = new_src
        reimported = import_video(bc)
        assert (
            self.repository['video']['2017-05']['myvid-still'].master_image
            == 'obama-clinton-120x120.jpg'
        )
        # but it does not change the reference of the video to the custom imagegroup
        img = zeit.content.image.interfaces.IImages(reimported.cmsobj)
        assert img.image.master_image == 'master-image.jpg'

    def test_update_teaser_image_sets_reference_if_vivi_has_none(self):
        src = 'http://{0.layer[http_address]}/testdata/opernball.jpg'.format(self)
        bc = create_video()
        bc.data['images']['poster']['src'] = src
        import_video(bc)
        # importing the video has created an image group "next to it" for its still image
        video = self.repository['video']['2017-05']['myvid']
        img = zeit.content.image.interfaces.IImages(video)
        assert img.image == self.repository['video']['2017-05']['myvid-still']

        with checked_out(video) as co:
            img = zeit.content.image.interfaces.IImages(co)
            img.images = None

        reimported = import_video(bc)
        img = zeit.content.image.interfaces.IImages(reimported.cmsobj)
        assert img.image == self.repository['video']['2017-05']['myvid-still']


class ExportTest(zeit.brightcove.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.repository['myvid'] = zeit.content.video.video.Video()
        self.request_patch = mock.patch('zeit.brightcove.connection.CMSAPI._request')
        self.request = self.request_patch.start()

    def tearDown(self):
        self.request_patch.stop()
        super().tearDown()

    def test_video_changes_are_written_to_brightcove_on_checkin(self):
        with zeit.cms.checkout.helper.checked_out(
            self.repository['myvid'], semantic_change=True
        ) as co:
            co.title = 'local change'
        transaction.commit()
        self.assertEqual(1, self.request.call_count)
        self.assertEqual('local change', self.request.call_args[1]['body']['name'])

    def test_changes_are_not_written_during_publish(self):
        zeit.cms.workflow.interfaces.IPublish(self.repository['myvid']).publish(background=False)
        self.assertEqual(False, self.request.called)

    def test_changes_are_not_written_if_disabled(self):
        FEATURE_TOGGLES.set('video_disable_export_on_checkin')
        with zeit.cms.checkout.helper.checked_out(self.repository['myvid']):
            pass
        transaction.commit()
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
