import zope.component

import json

from unittest.mock import patch

from zeit.speech.testing import BrowserTestCase, TTS_CREATED
from zeit.speech.interfaces import ISpeech


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
