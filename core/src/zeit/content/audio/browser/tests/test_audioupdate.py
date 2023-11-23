import zope.component
from zeit.content.audio.audio import Audio, PodcastEpisodeInfo
from zeit.content.audio.interfaces import Podcast

import zeit.content.audio.browser.audioupdate
import zeit.simplecast.interfaces
import zeit.simplecast.testing


class BrowserTestCase(zeit.content.audio.testing.BrowserTestCase):
    def create_audio(self):
        audio = Audio()
        audio.title = 'Podcast episode'
        audio.url = 'http://example.com/cats.mp3'
        audio.audio_type = 'podcast'
        audio.external_id = 1234
        podcast = Podcast('cat-jokes-pawdcast', 'Cat Jokes Pawdcast', '1234', 'Jokes about cats')
        PodcastEpisodeInfo(audio).podcast = podcast
        self.repository['audio'] = audio
        return audio

    def test_request_audio_update_unavailable_to_normal_user(self):
        self.create_audio()
        browser = self.browser
        browser.login('user', 'userpw')
        browser.open('/repository/audio')
        self.assertNotIn('...Update audio from simplecast...', browser.contents)

    def test_audio_is_updated(self):
        audio = self.create_audio()
        simplecast = zope.component.getUtility(zeit.simplecast.interfaces.ISimplecast)
        simplecast._fetch_episode.return_value = zeit.simplecast.testing.EPISODE_200
        browser = self.browser
        browser.login('producer', 'producerpw')
        browser.open('/repository/audio')
        link = browser.getLink('Update audio from simplecast')
        link.click()
        simplecast._update.assert_called_with(audio, zeit.simplecast.testing.EPISODE_200)

    def test_simplecast_request_failed_displays_error(self):
        self.create_audio()
        simplecast = zope.component.getUtility(zeit.simplecast.interfaces.ISimplecast)
        simplecast._fetch_episode.return_value = {}
        browser = self.browser
        browser.login('producer', 'producerpw')

        browser.open('/repository/audio')
        link = browser.getLink('Update audio from simplecast')
        link.click()
        self.assertEllipsis(
            '...We could not find a podcast episode for http://xml.zeit.de/audio...',
            browser.contents,
        )
