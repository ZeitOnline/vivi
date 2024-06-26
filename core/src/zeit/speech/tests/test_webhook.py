from unittest.mock import patch
from urllib.error import HTTPError
import copy
import json

import celery.exceptions
import pytest
import zope.component

from zeit.cms.checkout.interfaces import CheckinCheckoutError
from zeit.speech.interfaces import ISpeech
from zeit.speech.testing import TTS_CREATED, TTS_DELETED, BrowserTestCase


class TestWebhook(BrowserTestCase):
    def setUp(self):
        super().setUp()
        self.speech = zope.component.getUtility(ISpeech)

    def test_event_called(self):
        with patch.object(self.speech, 'update', return_value=None) as mock_update:
            self.browser.post(
                'http://localhost/@@speech_webhook',
                json.dumps(TTS_CREATED),
                'application/json',
            )
            mock_update.assert_called_with(TTS_CREATED)

    def test_event_raises_validation_error(self):
        with pytest.raises(HTTPError):
            self.browser.post(
                'http://localhost/@@speech_webhook',
                json.dumps({'event': 'AUDIO_CREATED'}),
                'application/json',
            )

    def test_event_raises_validation_error_if_checksum_is_missing(self):
        broken_event = copy.deepcopy(TTS_CREATED)
        broken_event['articlesAudio'][0].pop('checksum')
        with patch.object(self.speech, 'update', return_value=None):
            with pytest.raises(
                HTTPError, match='HTTP Error 400: Missing field checksum in payload:.+'
            ):
                self.browser.post(
                    'http://localhost/@@speech_webhook',
                    json.dumps(broken_event),
                    'application/json',
                )

    def test_retryable_error_is_retried(self):
        events = {'update': TTS_CREATED, 'delete': TTS_DELETED}
        self.browser.handleErrors = False
        for event, payload in events.items():
            with patch.object(self.speech, event, side_effect=CheckinCheckoutError('provoked')):
                with self.assertRaises(celery.exceptions.Retry):
                    self.browser.post(
                        'http://localhost/@@speech_webhook',
                        json.dumps(payload),
                        'application/json',
                    )

    def test_delete_event_called(self):
        with patch.object(self.speech, 'delete', return_value=None) as mock_delete:
            self.browser.post(
                'http://localhost/@@speech_webhook',
                json.dumps(TTS_DELETED),
                'application/json',
            )
            mock_delete.assert_called_with(TTS_DELETED)
