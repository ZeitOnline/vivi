import json
import logging

import opentelemetry.trace
import zope.app.appsetup.product
import zope.component

from zeit.cms.content.sources import FEATURE_TOGGLES
import zeit.cms.celery
import zeit.cms.tracing
import zeit.content.audio.audio
import zeit.simplecast.interfaces


log = logging.getLogger(__name__)


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
        data = json.loads(body)
        self.execute_task(data)

        current_span = opentelemetry.trace.get_current_span()
        current_span.set_attributes({'http.body': body})

    def execute_task(self, data: dict):
        SPEECH_WEBHOOK_TASK.delay(data, _principal_id_=self._principal)


@zeit.cms.celery.task(queue='speech')
def SPEECH_WEBHOOK_TASK(data: dict):
    speech = zope.component.getUtility(zeit.speech.interfaces.ISpeech)
    event = data.get('event')
    if event == 'AUDIO_CREATED':
        speech.update(data)
    else:
        log.info('Event %s not handled.', event)
