import gocept.async.tests
import mock
import zeit.brightcove.convert2
import zeit.brightcove.testing
import zeit.cms.testing
import zope.testbrowser.testing


class NotificationTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.brightcove.testing.BRIGHTCOVE_LAYER

    def test_creates_async_job_for_given_video_id(self):
        # View is available without authentication
        b = zope.testbrowser.testing.Browser()
        with mock.patch('zeit.brightcove.convert2.Video.find_by_id') as find:
            find.return_value = self.create_video()
            b.post('http://localhost/@@update_video',
                   '{"event": "video-change", "video": "myvid"}',
                   'application/x-javascript')
            with zeit.cms.testing.site(self.getRootFolder()):
                gocept.async.tests.process('brightcove')
            find.assert_called_with('myvid')

    def create_video(self):
        bc = zeit.brightcove.convert2.Video()
        bc.data = {
            'id': 'myvid',
            'created_at': '2017-05-15T08:24:55.916Z',
            'state': 'INACTIVE',
        }
        return bc
