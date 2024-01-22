from datetime import datetime
import copy
import unittest.mock as mock

import pytz

from zeit.cms.content.interfaces import ISemanticChange
from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.audio.interfaces import ISpeechInfo
from zeit.speech.connection import Speech
from zeit.speech.testing import TTS_CREATED, FunctionalTestCase


class TestSpeech(FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        self.repository.connector.search_result = [(self.article.uniqueId)]
        IPublishInfo(self.article).published = True
        IPublishInfo(self.article).date_first_released = datetime(2024, 1, 1, 0, 0, tzinfo=pytz.UTC)
        self.unique_id = f'http://xml.zeit.de/tts/2024-01/{TTS_CREATED["uuid"]}'

    def create_audio(self, data):
        self.repository.connector.search_result = [(self.article.uniqueId)]
        speech = Speech()
        with mock.patch('zeit.speech.connection.Speech._find', return_value=None):
            speech.update(data)
        self.repository.connector.search_result = []

    def test_audio_created(self):
        assert ICMSContent(self.unique_id, None) is None
        self.create_audio(TTS_CREATED)

        cms_tts = ICMSContent(self.unique_id)
        assert cms_tts.url == TTS_CREATED['articlesAudio'][0]['audioEntry']['url']
        assert cms_tts.duration == 65
        assert ISpeechInfo(cms_tts).article_uuid == TTS_CREATED['uuid']
        assert ISpeechInfo(cms_tts).checksum == TTS_CREATED['articlesAudio'][0]['checksum']
        assert (
            ISpeechInfo(cms_tts).preview_url == TTS_CREATED['articlesAudio'][1]['audioEntry']['url']
        )
        assert IPublishInfo(cms_tts).published, 'Publish you fool!'

    def _setup_speech_message(self, field, value):
        tts_created = copy.deepcopy(TTS_CREATED)
        tts_created['articlesAudio'][0][field] = value
        return tts_created

    def test_update_existing_tts_audio(self):
        self.create_audio(TTS_CREATED)
        cms_tts = ICMSContent(self.unique_id)
        created_time = ISemanticChange(cms_tts).last_semantic_change
        assert ISpeechInfo(cms_tts).checksum == TTS_CREATED['articlesAudio'][0]['checksum']
        self.repository.connector.search_result = [(cms_tts.uniqueId)]
        tts_msg = self._setup_speech_message('checksum', 'cookiesandcake')
        speech = Speech()
        speech.update(tts_msg)
        updated_time = ISemanticChange(cms_tts).last_semantic_change
        assert updated_time > created_time, 'Semantic time should be updated'
        assert ISpeechInfo(cms_tts).checksum == 'cookiesandcake', 'Update your checksum'
