from unittest import mock
import zeit.brightcove.convert
import zeit.brightcove.testing
import zeit.cms.testing
from zeit.brightcove import convert


class NotificationTest(zeit.brightcove.testing.BrowserTestCase):

    def test_runs_import_as_system_user(self):
        # View is available without authentication
        b = zeit.cms.testing.Browser(self.layer['wsgi_app'])
        with mock.patch.object(
                zeit.brightcove.update.import_video_async,
                '__call__') as import_video:
            b.post('http://localhost/@@update_video',
                   '{"event": "video-change", "video": "myvid"}',
                   'application/x-javascript')
            self.assertEqual('myvid', import_video.call_args[0][0])
            self.assertEqual(
                'zope.user', import_video.call_args[1]['_principal_id_'])

    def create_video(self):
        bc = zeit.brightcove.convert.Video()
        bc.data = {
            'id': 'myvid',
            'created_at': '2017-05-15T08:24:55.916Z',
            'state': 'INACTIVE',
        }
        return bc


class ImageGroupFromImage(zeit.content.image.testing.BrowserTestCase):

    def test_image_group_from_image(self):
        local_image = zeit.content.image.testing.create_local_image('opernball.jpg')
        convert.image_group_from_image(self.repository, 'group', local_image)
        b = self.browser
        b.handleErrors = False
        b.open('http://localhost/++skin++vivi/repository'
               '/group/@@metadata.html')
