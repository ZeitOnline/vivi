from zeit.content.audio.audio import Audio
import zeit.content.audio.testing


class AudioObjectDetails(zeit.content.audio.testing.BrowserTestCase):

    def test_displays_title(self):
        audio = Audio()
        audio.title = 'mytitle'
        self.repository['audio'] = audio
        b = self.browser
        b.open('/repository/audio/@@object-details')
        self.assertEllipsis('...mytitle...', b.contents)
