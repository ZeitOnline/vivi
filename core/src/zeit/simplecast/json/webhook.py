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
    webhook in the Simplecast API, and _they_ will call it each time a
    podcast or episode is added/changed/deleted.
    """

    @property
    def _principal(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.simplecast')
        return config['principal']

    def __call__(self):
        if not FEATURE_TOGGLES.find('simplecast_webhook'):
            return

        body = self.request.bodyStream.read(
            int(self.request['CONTENT_LENGTH']))
        log.info(body)
        data = json.loads(body).get('data')
        episode_id = data.get('episode_id')
        event = data.get('event')

        self.execute_task(
            event=event, episode_id=episode_id)

        current_span = opentelemetry.trace.get_current_span()
        current_span.set_attributes({'http.body': body})

    def execute_task(self, event, episode_id):
        SIMPLECAST_WEBHOOK_TASK.delay(
            event, episode_id, _principal_id_=self._principal)


@zeit.cms.celery.task(queue='simplecast')
def SIMPLECAST_WEBHOOK_TASK(event, episode_id):
    simplecast = zope.component.getUtility(
        zeit.simplecast.interfaces.ISimplecast)
    log.info('Received %s simplecast request for %s.', event, episode_id)
    synchronizing_events = (
        'episode_created', 'episode_updated',
        'episode_published', 'episode_unpublished',
        'episode_deleted')
    if event in synchronizing_events:
        simplecast.synchronize_episode(episode_id)
    else:
        log.info('Event %s not handled.', event)
