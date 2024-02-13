import json
import logging

import opentelemetry.trace
import zope.app.appsetup.product
import zope.component

from zeit.cms.content.sources import FEATURE_TOGGLES
import zeit.cms.celery
import zeit.cms.checkout.interfaces
import zeit.cms.tracing
import zeit.content.audio.audio
import zeit.speech.interfaces


log = logging.getLogger(__name__)


class InvalidSpeechMessageError(Exception):
    """An exception raised for incomplete speechbert messages."""


class Notification:
    """This view is a receiver for notification events. We register it as a
    webhook in the Speechbert API, and _they_ will call it each time a
    text to speech audio is added/changed/deleted.
    """

    @property
    def _principal(self):
        config = zope.app.appsetup.product.getProductConfiguration('zeit.speech')
        return config['principal']

    def __call__(self):
        if not FEATURE_TOGGLES.find('speech_webhook'):
            return

        body = self.request.bodyStream.read(int(self.request['CONTENT_LENGTH']))
        log.info(body)
        payload = json.loads(body)

        current_span = opentelemetry.trace.get_current_span()
        current_span.set_attributes({'http.body': body})

        try:
            validate_request(payload)
        except InvalidSpeechMessageError as e:
            self.request.response.setStatus(400, e)
            return
        self.execute_task(payload)

    def execute_task(self, payload: dict):
        SPEECH_WEBHOOK_TASK.delay(payload, _principal_id_=self._principal)


@zeit.cms.celery.task(bind=True, queue='speech')
def SPEECH_WEBHOOK_TASK(self, payload: dict):
    speech = zope.component.getUtility(zeit.speech.interfaces.ISpeech)
    try:
        if payload['event'] == 'AUDIO_CREATED':
            speech.update(payload)
        elif payload['event'] == 'AUDIO_DELETED':
            speech.delete(payload)
    except zeit.cms.checkout.interfaces.CheckinCheckoutError:
        config = zope.app.appsetup.product.getProductConfiguration('zeit.speech')
        self.retry(
            countdown=int(config['retry-delay-seconds']), max_retries=int(config['max-retries'])
        )


def validate_request(payload: dict):
    event_type = payload.get('event')
    uuid = payload.get('uuid') or payload.get('article_uuid')
    if not all([event_type, uuid]):
        raise InvalidSpeechMessageError(f'Missing field in payload: {payload}')
