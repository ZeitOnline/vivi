import logging

import grokcore.component as grok
import pendulum
import requests
import zope.app.appsetup.product
import zope.component

from zeit.cms.content.interfaces import ISemanticChange
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
from zeit.connector.search import SearchVar
from zeit.content.audio.interfaces import IAudio, IPodcastEpisodeInfo
import zeit.cms.checkout.helper
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.tracing
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

    def __init__(self, timeout=None):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.simplecast')
        self.api_url = config['simplecast-url']
        self.api_token = f"Bearer {config['simplecast-token']}"
        self.timeout = timeout or config.get('timeout', 1)

    def _request(self, request):
        verb, path = request.split(' ')
        url = f'{self.api_url}{path}'

        tracer = zope.component.getUtility(zeit.cms.interfaces.ITracer)
        with tracer.start_as_current_span('simplecast') as span:
            span.set_attributes({'http.url': url, 'http.method': verb})
            status_code = None
            try:
                response = requests.request(
                    verb.lower(), url,
                    headers={'Authorization': self.api_token},
                    timeout=self.timeout)
                status_code = response.status_code
                response_text = response.text
                response.raise_for_status()
                json = response.json()
            except requests.exceptions.JSONDecodeError as err:
                response_text = f"Invalid Json {err}: {response.text}"
                raise
            except requests.exceptions.RequestException as err:
                if not status_code:
                    status_code = getattr(err.response, 'status_code', 599)
                response_text = getattr(err.response, 'text', str(err))
                log.error(
                    '%s returned %s', request, status_code, exc_info=True)
                raise
            finally:
                zeit.cms.tracing.record_span(span, status_code, response_text)

            return json

    def _fetch_episode(self, episode_id):
        """Request episode data from simplecast, return json body"""
        return self._request(f'GET episodes/{episode_id}')

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
        audio.audio_type = 'podcast'
        for iface, properties in self._properties.items():
            obj = iface(audio)
            for vivi, simplecast in properties.items():
                setattr(obj, vivi, episode_data[simplecast])

        podcast_id = episode_data['podcast']['id']
        info = IPodcastEpisodeInfo(audio)
        info.podcast_id = podcast_id
        info.podcast = \
            IPodcastEpisodeInfo['podcast'].source(None).find_by_property(
                'external_id', episode_data['podcast']['id'])

        ISemanticChange(audio).last_semantic_change = pendulum.parse(
            episode_data['updated_at'])

    def create_episode(self, episode_id):
        episode_data = self._fetch_episode(episode_id)
        container = self.folder(episode_data['created_at'])
        audio = zeit.content.audio.audio.Audio()
        self._update_properties(episode_data, audio)
        container[episode_id] = audio
        log.info('Podcast Episode %s successfully created.', audio.uniqueId)

    def update_episode(self, episode_id):
        audio = self._find_existing_episode(episode_id)
        if not audio:
            self.create_episode(episode_id)
            return
        episode_data = self._fetch_episode(episode_id)
        with zeit.cms.checkout.helper.checked_out(audio) as episode:
            self._update_properties(episode_data, episode)
            log.info(
                'Podcast Episode %s successfully updated.',
                episode.uniqueId)

    def delete_episode(self, episode_id):
        audio = self._find_existing_episode(episode_id)
        if audio:
            if IPublishInfo(audio).published:
                IPublish(audio).retract(background=False)
            unique_id = audio.uniqueId
            del audio.__parent__[audio.__name__]
            self.__parent__ = None
            log.info('Podcast Episode %s successfully deleted.', unique_id)
        else:
            log.warning(
                'No podcast episode %s found. No episode deleted.',
                episode_id)

    def publish_episode(self, episode_id):
        # XXX good idea or will the publish
        # event trigger update event before?
        self.update_episode(episode_id)
        audio = self._find_existing_episode(episode_id)
        if audio:
            IPublish(audio).publish(background=False)
            log.info('Podcast Episode %s successfully published.',
                     audio.uniqueId)
        else:
            log.warning(
                'No podcast episode %s found. Unable to publish episode.',
                episode_id)

    def retract_episode(self, episode_id):
        audio = self._find_existing_episode(episode_id)
        if audio and IPublishInfo(audio).published:
            with zeit.cms.checkout.helper.checked_out(
                    audio, semantic_change=None, events=False) as co:
                IPodcastEpisodeInfo(co).is_published = False
            IPublish(audio).retract(background=False)
            log.info('Podcast Episode %s successfully retracted.',
                     audio.uniqueId)
        else:
            log.warning(
                'No podcast episode %s found. Unable to retract episode.',
                episode_id)
