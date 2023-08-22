import requests_mock
import zeit.content.audio.testing


class TestSimplecastRequest(zeit.content.audio.testing.BrowserTestCase):

    login_as = 'producer:producerpw'

    def test_add_audio(self):
        self.make_audio()
        m_simple = requests_mock.Mocker()
        episode_id = '1234'
        m_simple.get(
            f'https://testapi.simplecast.com/episodes/{episode_id}',
            json=self.json)
        url = (
            'https://injector.simplecastaudio.com/5678/episodes/1234/audio'
            '/128/default.mp3?awCollectionId=5678&awEpisodeId=1234')

        with m_simple:
            browser = self.browser
            browser.open(
                'http://localhost/++skin++vivi/repository/1234/'
                '@@simplecast.html')
            self.assertEllipsis(
                '...Title Cat Jokes Pawdcast...', browser.contents)
            self.assertEllipsis('...Url ...', browser.contents)
            browser.getControl('Request episode data').click()
            self.assertEllipsis(
                '...Title Cat Jokes Pawdcast', browser.contents)
            self.assertEllipsis(f'...Url {url}...', browser.contents)
