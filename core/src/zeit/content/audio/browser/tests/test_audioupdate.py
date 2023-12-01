import zope.component
from zeit.content.audio.testing import AudioBuilder, BrowserTestCase

import zeit.content.audio.browser.audioupdate
import zeit.simplecast.interfaces
import zeit.simplecast.testing


class AudioUpdateTest(BrowserTestCase):
    def test_request_audio_update_unavailable_to_normal_user(self):
        AudioBuilder().build(self.repository)
        browser = self.browser
        browser.login('user', 'userpw')
        browser.open('/repository/audio')
        self.assertNotIn('Update audio from simplecast', browser.contents)

    def test_request_audio_update_unavailable_for_checked_out_object(self):
        AudioBuilder().build(self.repository)
        browser = self.browser
        browser.login('producer', 'producerpw')
        browser.open('/repository/audio')
        link = browser.getLink('Checkout')
        link.click()
        self.assertNotIn('Update audio from simplecast', browser.contents)

    def test_audio_is_updated(self):
        audio = AudioBuilder().build(self.repository)
        simplecast = zope.component.getUtility(zeit.simplecast.interfaces.ISimplecast)
        simplecast.fetch_episode.return_value = zeit.simplecast.testing.EPISODE_200
        browser = self.browser
        browser.login('producer', 'producerpw')
        browser.open('/repository/audio')
        link = browser.getLink('Update audio from simplecast')
        link.click()
        simplecast.update.assert_called_with(audio, zeit.simplecast.testing.EPISODE_200)
        simplecast.publish.assert_called_once()

    def test_simplecast_request_failed_displays_error(self):
        AudioBuilder().build(self.repository)
        simplecast = zope.component.getUtility(zeit.simplecast.interfaces.ISimplecast)
        simplecast.fetch_episode.return_value = {}
        browser = self.browser
        browser.login('producer', 'producerpw')

        browser.open('/repository/audio')
        link = browser.getLink('Update audio from simplecast')
        link.click()
        self.assertEllipsis(
            '...We could not find a podcast episode for http://xml.zeit.de/audio...',
            browser.contents,
        )
