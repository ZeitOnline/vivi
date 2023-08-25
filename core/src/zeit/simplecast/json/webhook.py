import json
import logging
import zope.app.appsetup.product
import zeit.content.audio.audio
import zeit.simplecast.interfaces
import zeit.cms.checkout.helper
import zope.component

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

        body = json.loads(body)

        simplecast = zope.component.getUtility(
            zeit.simplecast.interfaces.ISimplecast)

        if body.get('event') == 'episode-create':
            info = simplecast.fetch_episode(body.get('element_id'))
            container = zeit.content.audio.audio.audio_container(create=True)
            zeit.content.audio.audio.add_audio(container, info)

        elif body.get('event') == 'episode-update':
            info = simplecast.fetch_episode(body.get('element_id'))
            container = zeit.content.audio.audio.audio_container()
            if container is not None:
                with zeit.cms.checkout.helper.checked_out(
                        container[body.get('element_id')]) as episode:
                    episode.update(info)

        elif body.get('event') == 'episode-delete':
            container = zeit.content.audio.audio.audio_container()
            if container is not None:
                zeit.content.audio.audio.remove_audio(
                    container[body.get('element_id')])
