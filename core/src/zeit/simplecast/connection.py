import logging
import grokcore.component as grok
import pendulum
import requests
import zope.app.appsetup.product

from zeit.connector.search import SearchVar

import zeit.cms.checkout.helper
import zeit.cms.repository.interfaces
import zeit.content.audio.audio
import zeit.simplecast.interfaces

log = logging.getLogger(__name__)


AUDIO_ID = SearchVar('episode_id', zeit.content.audio.audio.AUDIO_SCHEMA_NS)


@grok.implementer(zeit.simplecast.interfaces.ISimplecast)
class Simplecast(grok.GlobalUtility):

    def __init__(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.simplecast')
        self.api_url = config['simplecast-url']
        self.api_token = f"Bearer {config['simplecast-token']}"

    def _request(self, verb, path):
        url = f'{self.api_url}{path}'
        headers = {'Authorization': self.api_token}
        response = requests.request(verb.lower(), url, headers=headers)
        if response.status_code == 404:
            log.error((
                'We could not find the podcast you are looking for, %s.'
                'Path: %s'),
                response.status_code, path)

        return response

    def fetch_episode(self, episode_id):
        return self._request('GET', f'episodes/{episode_id}').json()

    def folder(self, episode_create_at):
        """Podcast should end up in this folder by default"""
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.simplecast')
        podcasts = config['podcast-folder']
        date_created = pendulum.parse(episode_create_at)
        yyyy_mm = date_created.strftime('%Y-%m')
        if podcasts not in repository:
            repository[podcasts] = zeit.cms.repository.folder.Folder()
        if yyyy_mm not in repository[podcasts]:
            repository[podcasts][yyyy_mm] = zeit.cms.repository.folder.Folder()
        return repository[podcasts][yyyy_mm]

    def find_existing_episode(self, episode_id):
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        result = list(connector.search(
            [AUDIO_ID], (AUDIO_ID == str(episode_id))))
        if not result:
            return None
        try:
            content = zeit.cms.interfaces.ICMSContent(result[0][0])
            log.debug('Audio %s found for %s.', content.uniqueId, episode_id)
            return content
        except TypeError as error:
            log.error(
                'Audio %s found for %s. But not found in DAV: %s',
                result[0][0], episode_id, error
            )
            return None

    def create_episode(self, episode_id):
        info = self.fetch_episode(episode_id)
        container = self.folder(info['created_at'])
        audio = zeit.content.audio.audio.add_audio(container, info)
        log.info('Audio %s successfully created.', audio.uniqueId)

    def update_episode(self, episode_id):
        info = self.fetch_episode(episode_id)
        container = self.folder(info['created_at'])
        if container is not None:
            with zeit.cms.checkout.helper.checked_out(
                    container[episode_id]) as episode:
                episode.update(info)
                log.info(
                    'Audio %s successfully updated.', episode.uniqueId)

    def delete_episode(self, episode_id):
        audio = self.find_existing_episode(episode_id)
        if audio:
            unique_id = audio.uniqueId
            zeit.content.audio.audio.remove_audio(audio)
            log.info('Audio %s successfully deleted.', unique_id)
        else:
            log.warning(
                'No podcast episode %s found. No episode deleted.',
                episode_id)
