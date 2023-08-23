import json
import logging
import zope.app.appsetup.product
import zeit.content.audio.audio
import zeit.content.audio.interfaces
import zeit.cms.repository.folder
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
            zeit.content.audio.interfaces.ISimplecast)

        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

        if body.get('event') == 'episode-create':
            info = simplecast.fetch_episode(body.get('element_id'))

            if 'audios' not in repository:
                repository['audios'] = zeit.cms.repository.folder.Folder()

            zeit.content.audio.audio.add_audio(
                repository['audios'], info)

        elif body.get('event') == 'episode-update':
            info = simplecast.fetch_episode(body.get('element_id'))

            if 'audios' in repository:
                with zeit.cms.checkout.helper.checked_out(
                        repository['audios'][info['id']]) as episode:
                    episode.title = info['title']
                    episode.url = info['audio_file_url']

        elif body.get('event') == 'episode-delete':
            if 'audios' in repository:
                del repository['audios'][body.get('element_id')]
