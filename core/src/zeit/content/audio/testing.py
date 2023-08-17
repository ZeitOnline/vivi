import zeit.cms.testing


product_config = """\
<product-config zeit.content.audio>
  simplecast-url https://testapi.simplecast.com/
</product-config>
"""

CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    product_config,
    bases=(zeit.cms.testing.CONFIG_LAYER,))
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZOPE_LAYER

    @property
    def json(self):
        return {
            "title": "Cat Jokes Pawdcast",
            "id": "1234",
            "audio_file_url": (
                "https://injector.simplecastaudio.com/5678/episodes/1234/audio"
                "/128/default.mp3?awCollectionId=5678&awEpisodeId=1234"),
            "ad_free_audio_file_url": None,
            "duration": 666,
        }
