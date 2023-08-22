import zeit.content.audio.testing


class TestAudio(zeit.content.audio.testing.BrowserTestCase):

    def test_add_audio(self):
        browser = self.browser
        browser.open(
            'http://localhost/++skin++vivi/repository/online/2007/01/')
        menu = browser.getControl(name='add_menu')
        menu.displayValue = ['Audio']
        browser.open(menu.value[0])
        browser.getControl('Title').value = 'Cats episode'
        browser.getControl('Episode Id').value = '1234'
        browser.getControl('File name').value = 'test-audio'
        browser.getControl('Add').click()
        self.assertNotIn('There were errors', browser.contents)
        browser.getLink('Checkin').click()
        self.assertEllipsis('...Cats episode...', browser.contents)
