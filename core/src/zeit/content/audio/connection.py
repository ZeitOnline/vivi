import grokcore.component as grok
import logging
import requests
import zope.app.appsetup.product

import zeit.content.audio.interfaces


log = logging.getLogger(__name__)


@grok.implementer(zeit.content.audio.interfaces.ISimplecast)
class Simplecast(grok.GlobalUtility):

    def __init__(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.audio')
        self.api_url = config['simplecast-url']

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
        response = requests.request(verb.lower(), url)
        if response.status_code == 404:
            log.error((
                'We could not find the podcast you are looking for, %s.'
                'Path: %s'),
                response.status_code, path)

        return response
