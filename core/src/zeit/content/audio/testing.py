import zeit.cms.testing
import zeit.content.audio.audio


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    bases=(zeit.cms.testing.CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))

JSON = {
    "title": "Cat Jokes Pawdcast",
    "id": "1234",
    "audio_file_url": (
        "https://injector.simplecastaudio.com/5678/episodes/1234/audio"
        "/128/default.mp3?awCollectionId=5678&awEpisodeId=1234"),
    "ad_free_audio_file_url": None,
    "created_at": "2023-08-31T13:51:00-01:00",
    "duration": 666,
}


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):

    layer = WSGI_LAYER
    json = JSON

    def make_audio(self):
        audio = zeit.content.audio.audio.Audio()
        audio.title = self.json['title']
        audio.episode_id = self.json['id']
        audio.url = self.json['audio_file_url']
        self.repository[audio.episode_id] = audio
