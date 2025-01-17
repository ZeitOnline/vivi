import zeit.cms.testing
import zeit.content.video.testing
import zeit.content.video.video


class VideoFormTest(zeit.content.video.testing.BrowserTestCase):
    def test_edit_video(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            video = zeit.content.video.video.Video()
            video.external_id = '1234'
            self.repository['video'] = video

        b = self.browser
        b.open('http://localhost/repository/video')
        b.getLink('Checkout').click()

        b.getControl('Title').value = 'Video title'
        b.getControl('Product').displayValue = ['Die Zeit']
        b.getControl('Ressort').displayValue = ['Deutschland']
        b.getControl(
            name='form.keywords'
        ).value = '[{"code": "tag://test\\\\u2603Testtag", "pinned": false}]'
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)

        b.getLink('Checkin').click()
        self.assertEllipsis('..."video" has been checked in...', b.contents)
