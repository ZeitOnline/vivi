from unittest.mock import patch
import json

import zope.component

from zeit.speech.interfaces import ISpeech
from zeit.speech.testing import TTS_CREATED, BrowserTestCase


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
