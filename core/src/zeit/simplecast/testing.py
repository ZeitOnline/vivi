import zeit.cms.testing


product_config = """\
<product-config zeit.simplecast>
  simplecast-url https://testapi.simplecast.com/
  simplecast-token TkQvZUd2MHRnR0UybFhsgTfs
</product-config>
"""

CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    product_config,
    bases=(zeit.cms.testing.CONFIG_LAYER,))
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))

EPISODE_INFO = {
    "title": "Episode 42",
    "id": "b44b1838-4ff4-4c29-ba1c-9c4f4b863eac",
    "audio_file_url": (
        "https://injector.simplecastaudio.com/"
        "04b0bba3-e114-4d7a-bf27-c398dcff13fd/episodes/"
        "b44b1838-4ff4-4c29-ba1c-9c4f4b863eac/audio/128/default.mp3"
        "?awCollectionId=04b0bba3-e114-4d7a-bf27-c398dcff13fd"
        "&awEpisodeId=b44b1838-4ff4-4c29-ba1c-9c4f4b863eac"),
    "ad_free_audio_file_url": (
        "https://cdn.simplecast.com/audio/"
        "04b0bba3-e114-4d7a-bf27-c398dcff13fd/episodes/"
        "b44b1838-4ff4-4c29-ba1c-9c4f4b863eac/audio/"
        "2123a65c-e415-4640-b1f1-108d3029a856/default_tc.mp3"),
    "duration": 663,
    "created_at": "2023-08-31T13:51:00-01:00"
}


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZOPE_LAYER
    episode_info = EPISODE_INFO


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):

    layer = WSGI_LAYER
    episode_info = EPISODE_INFO
