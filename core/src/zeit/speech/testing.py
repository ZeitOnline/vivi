import zeit.cms.testing
import zeit.content.audio.testing
import zeit.workflow.testing


product_config = """\
<product-config zeit.speech>
  principal zope.speech
  speech-folder tts
</product-config>
"""


TTS_CREATION_STARTED = {
    'event': 'AUDIO_CREATION_STARTED',
    'uuid': 'a89ce2e3-4887-466a-a52e-edc6b9802ef9',
    'checksum': '3c5977f672b95b3c5abad925b381437c6ca818f4',
}

TTS_CREATION_FAILED = {
    'event': 'AUDIO_CREATION_FAILED',
    'uuid': 'a89ce2e3-4887-466a-a52e-edc6b9802ef9',
    'checksum': '3c5977f672b95b3c5abad925b381437c6ca818f4',
    'reason': 'AudioStream must be a Buffer',
}

TTS_CREATED = {
    'event': 'AUDIO_CREATED',
    'uuid': 'a89ce2e3-4887-466a-a52e-edc6b9802ef9',
    'articlesAudio': [
        {
            'type': 'FULL_TTS',
            'checksum': '3c5977f672b95b3c5abad925b381437c6ca818f4',
            'audioEntry': {
                'uuid': 'e7fba272-c442-4cde-a5c9-3d75a89e5273',
                'url': 'https://zon-speechbert/articles/a89ce2e3-4887-466a-a52e-edc6b9802ef9/full_1fd74183d02f50d5cd0731a5748019e95bbe68bd71f33cbd2c03c4d64c8a1d91a7f25f6725db6b19348bd94af09fc563.mp3',
                'duration': 65000,
            },
        },
        {
            'type': 'PREVIEW_TTS',
            'checksum': '3c5977f672b95b3c5abad925b381437c6ca818f4',
            'audioEntry': {
                'uuid': '58ff08f4-cef5-45eb-a980-064bd78c42df',
                'url': 'https://zon-speechbert/articles/a89ce2e3-4887-466a-a52e-edc6b9802ef9/preview_1fd74183d02f50d5cd0731a5748019e95bbe68bd71f33cbd2c03c4d64c8a1d91a7f25f6725db6b19348bd94af09fc563.mp3',
                'duration': 15000,
            },
        },
    ],
}

TTS_DELETED = {
    'event': 'AUDIO_DELETED',
    'uuid': 'a89ce2e3-4887-466a-a52e-edc6b9802ef9',
}

CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    product_config,
    bases=(zeit.content.audio.testing.CONFIG_LAYER, zeit.workflow.testing.CONFIG_LAYER),
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting.zcml', bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER
