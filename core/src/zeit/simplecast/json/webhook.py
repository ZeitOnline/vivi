import json
import logging
import zope.app.appsetup.product
import zeit.content.audio.audio
import zeit.simplecast.interfaces
import zope.component

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

    @property
    def environment(self):
        config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
        return config['environment']

    def __call__(self):
        # XXX Do nothing in production until we know how to tell
        # notifications apart
        if self.environment not in ('staging', 'testing'):
            return

        body = self.request.bodyStream.read(
            int(self.request['CONTENT_LENGTH']))
        log.info(body)

        body = json.loads(body).get('data')
        episode_id = body.get('episode_id')
        event = body.get('event')

        self.execute_task(
            event=event, episode_id=episode_id)

    def execute_task(self, event, episode_id):
        SIMPLECAST_WEBHOOK_TASK.delay(
            event, episode_id, _principal_id_=self._principal)


@zeit.cms.celery.task(queue='simplecast')
def SIMPLECAST_WEBHOOK_TASK(event, episode_id):
    simplecast = zope.component.getUtility(
        zeit.simplecast.interfaces.ISimplecast)

    if event == 'episode_created':
        log.info('Create episode from simplecast request.')
        simplecast.create_episode(episode_id)

    elif event == 'episode_updated':
        log.info('Update episode from simplecast request.')
        simplecast.update_episode(episode_id)

    elif event == 'episode_deleted':
        log.info('Delete episode from simplecast request.')
        simplecast.delete_episode(episode_id)

    else:
        log.info('No episode processed.')
