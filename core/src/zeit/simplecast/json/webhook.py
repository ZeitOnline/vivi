import json
import logging

import opentelemetry.trace
import zope.component

from zeit.cms.content.sources import FEATURE_TOGGLES
import zeit.cms.celery
import zeit.cms.config
import zeit.cms.tracing
import zeit.content.audio.audio
import zeit.simplecast.interfaces


log = logging.getLogger(__name__)


class Notification:
    """This view is a receiver for notification events. We register it as a
    webhook in the Simplecast API, and _they_ will call it each time a
    podcast or episode is added/changed/deleted.
    """

    @property
    def _principal(self):
        return zeit.cms.config.required('zeit.simplecast', 'principal')

    def __call__(self):
        if not FEATURE_TOGGLES.find('simplecast_webhook'):
            return

        body = self.request.bodyStream.read(int(self.request['CONTENT_LENGTH']))
        log.info(body)
        data = json.loads(body).get('data', {})
        self.execute_task(data)

        current_span = opentelemetry.trace.get_current_span()
        current_span.set_attributes({'http.body': body})

    def execute_task(self, data: dict):
        SIMPLECAST_WEBHOOK_TASK.delay(data, _principal_id_=self._principal)


@zeit.cms.celery.task(bind=True, queue='simplecast')
def SIMPLECAST_WEBHOOK_TASK(self, data: dict):
    simplecast = zope.component.getUtility(zeit.simplecast.interfaces.ISimplecast)
    episode_id = data.get('episode_id')
    if not episode_id:
        # transcode_finished event does not contain episode_id
        episode_audio_id = data.get('episode_audio_id')
        if episode_audio_id:
            audio_data = simplecast.fetch_episode_audio(episode_audio_id)
            if audio_data:
                episode_id = audio_data.get('episode_id')

    event = data.get('event')
    if not episode_id:
        log.info('Received %s simplecast request without episode_id.', event)
        return

    log.info('Received %s simplecast request for %s.', event, episode_id)
    synchronizing_events = (
        'episode_created',
        'episode_deleted',
        'episode_published',
        'episode_unpublished',
        'episode_updated',
        'transcode_finished',
    )
    if event in synchronizing_events:
        try:
            simplecast.synchronize_episode(episode_id)
        except zeit.simplecast.interfaces.TechnicalError:
            config = zeit.cms.config.package('zeit.simplecast')
            self.retry(countdown=int(config['retry-delay-seconds']))
    else:
        log.info('Event %s not handled.', event)
