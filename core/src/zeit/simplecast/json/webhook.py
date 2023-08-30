import json
import logging
import zope.app.appsetup.product
import zeit.content.audio.audio
import zeit.simplecast.interfaces
import zeit.cms.checkout.helper
import zope.component
import celery.result
import celery.states

log = logging.getLogger(__name__)


class Notification:
    """This view is a receiver for notification events. We register it as a
    webhook in the Simplecast API, and _they_ will call it each time a
    podcast or episode is added/changed/deleted.
    """

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

        # SIMPLECAST_WEBHOOK_TASK.apply_async(body)
        result = SIMPLECAST_WEBHOOK_TASK(body)
        celery.result.EagerResult('eager', result, celery.states.SUCCESS)


@zeit.cms.celery.task
def SIMPLECAST_WEBHOOK_TASK(body):
    simplecast = zope.component.getUtility(
        zeit.simplecast.interfaces.ISimplecast)
    log.info('Simplecast utility %s', simplecast)

    if body.get('event') == 'episode_created':
        log.info('Create episode from simplecast request.')
        info = simplecast.fetch_episode(body.get('episode_id'))
        container = zeit.content.audio.audio.audio_container(create=True)
        zeit.content.audio.audio.add_audio(container, info)

    elif body.get('event') == 'episode_updated':
        log.info('Update episode from simplecast request.')
        info = simplecast.fetch_episode(body.get('episode_id'))
        container = zeit.content.audio.audio.audio_container()
        if container is not None:
            with zeit.cms.checkout.helper.checked_out(
                    container[body.get('episode_id')]) as episode:
                episode.update(info)

    elif body.get('event') == 'episode_deleted':
        log.info('Delete episode from simplecast request.')
        container = zeit.content.audio.audio.audio_container()
        if container is not None:
            zeit.content.audio.audio.remove_audio(
                container[body.get('episode_id')])
    else:
        log.info('No episode processed.')
