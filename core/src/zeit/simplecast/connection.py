import logging
import grokcore.component as grok
import requests
import zope.app.appsetup.product

import zeit.cms.repository.interfaces
import zeit.simplecast.interfaces

log = logging.getLogger(__name__)


@grok.implementer(zeit.simplecast.interfaces.ISimplecast)
class Simplecast(grok.GlobalUtility):

    def __init__(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.simplecast')
        self.api_url = config['simplecast-url']
        self.api_token = f"Bearer {config['simplecast-token']}"

    def get_episode(self, episode_id):
        response = self._request('GET', f'episodes/{episode_id}')
        try:
            title = response.json()['title']
            url = response.json()['audio_file_url']
            duration = response.json()['duration']
            return url, duration, title
        except KeyError:
            log.error('Episode information is not available.')
            raise

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
        podcasts = 'podcasts'
        # Select year and month from string instead of parsing YYYY-MM with
        # pendulum and converting it back to the correct format
        yyyy_mm = episode_create_at[0:7]
        if podcasts not in repository:
            repository[podcasts] = zeit.cms.repository.folder.Folder()
        if yyyy_mm not in repository[podcasts]:
            repository[podcasts][yyyy_mm] = zeit.cms.repository.folder.Folder()
        return repository[podcasts][yyyy_mm]
