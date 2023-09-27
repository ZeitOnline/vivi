from zeit.connector.search import SearchVar
from zeit.content.audio.interfaces import (
    IAudio, IPodcastEpisodeInfo)
import logging

import grokcore.component as grok
import pendulum
import requests
import zope.app.appsetup.product

import zeit.cms.checkout.helper
import zeit.cms.repository.interfaces
import zeit.content.audio.audio
import zeit.simplecast.interfaces

log = logging.getLogger(__name__)

AUDIO_ID = SearchVar('external_id', zeit.content.audio.audio.AUDIO_SCHEMA_NS)


@grok.implementer(zeit.simplecast.interfaces.ISimplecast)
class Simplecast(grok.GlobalUtility):

    #: lazy mapping between audio interfaces (key) and simplecast api (value)
    _properties = {
        IAudio: {
            'title': 'title',
            'url': 'audio_file_url',
            'duration': 'duration',
            'external_id': 'id',
        },
        IPodcastEpisodeInfo: {
            'episode_nr': 'number',
            'summary': 'description',
            'notes': 'long_description',
            'is_published': 'is_published',
        }
    }

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

    def _fetch_episode(self, episode_id):
        """Request episode data from simplecast, return json body"""
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

    def _find_existing_episode(self, episode_id):
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        result = list(connector.search(
            [AUDIO_ID], (AUDIO_ID == str(episode_id))))
        if not result:
            return None
        try:
            content = zeit.cms.interfaces.ICMSContent(result[0][0])
            log.debug('Podcast %s found for %s.', content.uniqueId, episode_id)
            return content
        except TypeError as error:
            log.error(
                'Podcast Episode %s found for %s. But not found in DAV: %s',
                result[0][0], episode_id, error
            )
            return None

    def _update_properties(self, episode_data, audio):
        for iface, properties in self._properties.items():
            obj = iface(audio)
            for vivi, simplecast in properties.items():
                setattr(obj, vivi, episode_data[simplecast])

        IPodcastEpisodeInfo(audio).podcast = \
            IPodcastEpisodeInfo['podcast'].source(None).find_by_property(
                'external_id', episode_data['podcast']['id'])

    def create_episode(self, episode_id):
        episode_data = self._fetch_episode(episode_id)
        container = self.folder(episode_data['created_at'])
        audio = zeit.content.audio.audio.Audio()
        audio.audio_type = 'podcast'
        self._update_properties(episode_data, audio)
        container[episode_id] = audio
        log.info('Podcast Episode %s successfully created.', audio.uniqueId)

    def update_episode(self, episode_id):
        episode_data = self._fetch_episode(episode_id)
        container = self.folder(episode_data['created_at'])
        if container is not None:
            with zeit.cms.checkout.helper.checked_out(
                    container[episode_id]) as episode:
                self._update_properties(episode_data, episode)
                log.info(
                    'Podcast Episode %s successfully updated.',
                    episode.uniqueId)

    def delete_episode(self, episode_id):
        audio = self._find_existing_episode(episode_id)
        if audio:
            unique_id = audio.uniqueId
            del audio.__parent__[audio.__name__]
            self.__parent__ = None
            log.info('Podcast Episode %s successfully deleted.', unique_id)
        else:
            log.warning(
                'No podcast episode %s found. No episode deleted.',
                episode_id)
