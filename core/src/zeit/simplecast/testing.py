import zeit.cms.testing
import zeit.content.audio.testing


EPISODE_200 = {
    'created_at': '2023-08-31T13:51:00-01:00',
    'description': 'lorem ipsum',
    'duration': 666,
    'id': '1234',
    'long_description': 'lorem ipsum dolor sit amet',
    'number': 2,
    'title': 'Cat Jokes Pawdcast',
    'is_published': False,
    'updated_at': '2020-07-13T14:21:39+00:00',
    'audio_file_url': (
        'https://injector.simplecastaudio.com/'
        '04b0bba3-e114-4d7a-bf27-c398dcff13fd/episodes/'
        'b44b1838-4ff4-4c29-ba1c-9c4f4b863eac/audio/128/default.mp3'
        '?awCollectionId=04b0bba3-e114-4d7a-bf27-c398dcff13fd'
        '&awEpisodeId=b44b1838-4ff4-4c29-ba1c-9c4f4b863eac'
    ),
    'ad_free_audio_file_url': (
        'https://cdn.simplecast.com/audio/'
        '04b0bba3-e114-4d7a-bf27-c398dcff13fd/episodes/'
        'b44b1838-4ff4-4c29-ba1c-9c4f4b863eac/audio/'
        '2123a65c-e415-4640-b1f1-108d3029a856/default_tc.mp3'
    ),
    'podcast': {
        'id': '1234',
        'href': 'https://api.simplecast.com/podcasts/c3161c7d-d5ac-46a9-82c1-b18cbcc93b5c',
        'title': 'Cat Jokes Pawdcast',
        'status': 'published',
    },
    'dashboard_link': (
        'https://dashboard.simplecast.com/'
        'accounts/cf104b97-1579-49fb-a545-05f7e578a594/'
        'shows/60989a9e-80b6-4f17-979a-fc949043cf6b/'
        'episodes/8e73a60a-87c9-4b6b-8f92-96152cc4b315'
    ),
}

CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'simplecast-url': 'https://testapi.simplecast.com/',
        'simplecast-token': 'TkQvZUd2MHRnR0UybFhsgTfs',
        'podcast-folder': 'podcasts',
        'principal': 'zope.simplecast',
        'retry-delay-seconds': '0',
    },
    bases=(zeit.content.audio.testing.CONFIG_LAYER,),
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting.zcml', bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER
    episode_info = EPISODE_200

    def setUp(self):
        super().setUp()
        self.repository.connector.search_result = []


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER
    episode_info = EPISODE_200

    def setUp(self):
        super().setUp()
        self.repository.connector.search_result = []
