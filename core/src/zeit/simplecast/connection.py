from zeit.connector.search import SearchVar

import grokcore.component as grok
import logging
import pendulum
import requests
import zope.app.appsetup.product
import zope.component

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


@grok.implementer(zeit.simplecast.interfaces.IConnector)
class Connector(grok.Adapter):

    grok.context(zeit.content.audio.interfaces.IAudio)

    def request(self, context):
        simplecast = zope.component.getUtility(
            zeit.simplecast.interfaces.ISimplecast)
        (url, duration, title) = simplecast.get_episode(context.episodeId)
        context = zope.security.proxy.removeSecurityProxy(context)
        context.title = title
        context.url = url
        context.duration = duration
