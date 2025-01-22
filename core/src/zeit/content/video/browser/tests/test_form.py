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

    def test_add_video(self):
        b = self.browser
        b.open('http://localhost/repository')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Video']
        b.open(menu.value[0])
        self.assertEllipsis('...Add Video...', b.contents)
        b.getControl('File name').value = 'myvideo'
        b.getControl('Video platform').displayValue = ['Youtube']
        b.getControl('Title').value = 'myvid'
        b.getControl('External ID').value = '1234'
        b.getControl('Ressort').displayValue = ['Deutschland']
        b.getControl('Markdown content').value = '# my title'
        b.getControl(name='form.actions.add').click()
        self.assertEllipsis('...Edit Video...', b.contents)
        b.getLink('Checkin').click()
        self.assertEllipsis('..."myvideo" has been checked in...', b.contents)
        self.assertEllipsis('...External ID...1234...', b.contents)
        self.assertEllipsis('...<h1>my title</h1>...', b.contents)
