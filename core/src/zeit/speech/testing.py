from datetime import datetime
import copy
import unittest.mock as mock

import pytest

from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
from zeit.speech.connection import Speech
import zeit.cms.testing
import zeit.content.article.testing
import zeit.content.audio.testing


product_config = """\
<product-config zeit.speech>
  principal zope.speech
  speech-folder tts
  retry-delay-seconds 0
</product-config>
"""


TTS_CREATION_STARTED = {
    'event': 'AUDIO_CREATION_STARTED',
    'uuid': 'a89ce2e3-4887-466a-a52e-edc6b9802ef9',
    'checksum': 'd751713988987e9331980363e24189ce',
}

TTS_CREATION_FAILED = {
    'event': 'AUDIO_CREATION_FAILED',
    'uuid': 'a89ce2e3-4887-466a-a52e-edc6b9802ef9',
    'checksum': 'd751713988987e9331980363e24189ce',
    'reason': 'AudioStream must be a Buffer',
}

TTS_CREATED = {
    'event': 'AUDIO_CREATED',
    'uuid': 'a89ce2e3-4887-466a-a52e-edc6b9802ef9',
    'articlesAudio': [
        {
            'type': 'FULL_TTS',
            'checksum': 'd751713988987e9331980363e24189ce',
            'audioEntry': {
                'uuid': 'e7fba272-c442-4cde-a5c9-3d75a89e5273',
                'url': 'https://zon-speechbert/articles/a89ce2e3-4887-466a-a52e-edc6b9802ef9/full_1fd74183d02f50d5cd0731a5748019e95bbe68bd71f33cbd2c03c4d64c8a1d91a7f25f6725db6b19348bd94af09fc563.mp3',
                'duration': 65000,
            },
        },
        {
            'type': 'PREVIEW_TTS',
            'checksum': 'd751713988987e9331980363e24189ce',
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
    'article_uuid': 'a89ce2e3-4887-466a-a52e-edc6b9802ef9',
    'audio_uuid:': 'a89ab2e3-4777-466a-a51a-edc6b9802ef1',
}

CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    product_config,
    bases=(zeit.content.article.testing.CONFIG_LAYER,),
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting.zcml', bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER

    def setUp(self):
        super().setUp()
        current_date = datetime.now()
        self.unique_id = (
            f'http://xml.zeit.de/tts/{current_date.strftime("%Y-%m")}/{TTS_CREATED["uuid"]}'
        )
        self.article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        self.article_uid = 'http://xml.zeit.de/online/2007/01/Somalia'
        IPublishInfo(self.article).urgent = True
        IPublish(self.article).publish(background=False)

    def tearDown(self):
        self.caplog.clear()

    @pytest.fixture(autouse=True)
    def _caplog(self, caplog):
        self.caplog = caplog

    def create_audio(self, data):
        self.repository.connector.search_result = [(self.article.uniqueId)]
        speech = Speech()
        with mock.patch('zeit.speech.connection.Speech._find', return_value=None):
            speech.update(data)
        self.repository.connector.search_result = []
        return ICMSContent(self.unique_id)

    def setup_speech_message(self, field, value):
        tts_created = copy.deepcopy(TTS_CREATED)
        tts_created['articlesAudio'][0][field] = value
        return tts_created


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER
