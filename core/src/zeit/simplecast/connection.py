import logging

import pendulum
import requests
import zope.app.appsetup.product
import zope.component
import zope.interface

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


@zope.interface.implementer(zeit.simplecast.interfaces.ISimplecast)
class Simplecast:
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
            'url_ad_free': 'ad_free_audio_file_url',
            'summary': 'description',
            'notes': 'long_description',
            'is_published': 'is_published',
            'dashboard_link': 'dashboard_link',
        },
    }

    def __init__(self, timeout=None):
        config = zope.app.appsetup.product.getProductConfiguration('zeit.simplecast')
        self.api_url = config['simplecast-url']
        self.api_token = f"Bearer {config['simplecast-token']}"
        self.timeout = timeout or int(config.get('timeout', 1))

    def _request(self, request):
        verb, path = request.split(' ')
        url = f'{self.api_url}{path}'

        tracer = zope.component.getUtility(zeit.cms.interfaces.ITracer)
        with tracer.start_as_current_span('simplecast') as span:
            span.set_attributes({'http.url': url, 'http.method': verb})
            status_code = None
            try:
                response = requests.request(
                    verb.lower(),
                    url,
                    headers={'Authorization': self.api_token},
                    timeout=self.timeout,
                )
                status_code = response.status_code
                response_text = response.text
                # 404 is a valid response
                # will trigger delete if audio exist
                if status_code == 404:
                    return None
                response.raise_for_status()
                json = response.json()
            except requests.exceptions.JSONDecodeError as err:
                response_text = f'Invalid Json {err}: {response.text}'
                raise
            except requests.exceptions.RequestException as err:
                if not status_code:
                    status_code = getattr(err.response, 'status_code', 599)
                response_text = getattr(err.response, 'text', str(err))
                log.error('%s returned %s', request, status_code, exc_info=True)
                raise
            finally:
                zeit.cms.tracing.record_span(span, status_code, response_text)

            return json

    def fetch_episode_audio(self, audio_id):
        return self._request(f'GET episodes/audio/{audio_id}')

    def fetch_episode(self, episode_id):
        """Request episode data from simplecast, return json body"""
        return self._request(f'GET episodes/{episode_id}')

    def folder(self, episode_create_at):
        """Podcast should end up in this folder by default"""
        repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        config = zope.app.appsetup.product.getProductConfiguration('zeit.simplecast')
        podcasts = config['podcast-folder']
        date_created = pendulum.parse(episode_create_at)
        yyyy_mm = date_created.strftime('%Y-%m')
        if podcasts not in repository:
            repository[podcasts] = zeit.cms.repository.folder.Folder()
        if yyyy_mm not in repository[podcasts]:
            repository[podcasts][yyyy_mm] = zeit.cms.repository.folder.Folder()
        return repository[podcasts][yyyy_mm]

    def _find_existing_episode(self, episode_id):
        connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
        result = list(connector.search([AUDIO_ID], (AUDIO_ID == str(episode_id))))
        if not result:
            return None
        try:
            content = zeit.cms.interfaces.ICMSContent(result[0][0])
            log.debug('Podcast %s found for %s.', content.uniqueId, episode_id)
            return content
        except TypeError as error:
            log.error(
                'Podcast Episode %s found for %s. But not found in DAV: %s',
                result[0][0],
                episode_id,
                error,
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
        info.podcast = (
            IPodcastEpisodeInfo['podcast']
            .source(None)
            .find_by_property('external_id', episode_data['podcast']['id'])
        )

        ISemanticChange(audio).last_semantic_change = pendulum.parse(episode_data['updated_at'])

    def synchronize_episode(self, episode_id):
        audio = self._find_existing_episode(episode_id)
        episode_data = self.fetch_episode(episode_id)
        if audio and episode_data:
            self.update(audio, episode_data)
        elif not audio and episode_data:
            audio = self._create(episode_id, episode_data)
        elif audio and not episode_data:
            self._delete(audio)
            return
        elif not audio and not episode_data:
            log.warning('No podcast episode %s in vivi and simplecast found.', episode_id)
            return

        if self._publish_state_needs_sync(audio):
            self.publish(audio)
        elif self._retract_state_needs_sync(audio):
            self._retract(audio)

    def _retract_state_needs_sync(self, audio):
        return IPublishInfo(audio).published and not IPodcastEpisodeInfo(audio).is_published

    def _publish_state_needs_sync(self, audio):
        return IPodcastEpisodeInfo(audio).is_published

    def _create(self, episode_id, episode_data):
        container = self.folder(episode_data['created_at'])
        audio = zeit.content.audio.audio.Audio()
        self._update_properties(episode_data, audio)
        container[episode_id] = audio
        log.info('Podcast Episode %s successfully created.', audio.uniqueId)
        return container[episode_id]

    def update(self, audio, episode_data):
        with zeit.cms.checkout.helper.checked_out(audio) as episode:
            if not episode:
                log.error('Unable to update %s. Could not checkout!', audio.uniqueId)
                return

            self._update_properties(episode_data, episode)
            log.info('Podcast Episode %s successfully updated.', episode.uniqueId)

    def publish(self, audio):
        IPublish(audio).publish(background=False)
        log.info('Podcast Episode %s successfully published.', audio.uniqueId)

    def _retract(self, audio):
        with zeit.cms.checkout.helper.checked_out(audio, semantic_change=None, events=False) as co:
            IPodcastEpisodeInfo(co).is_published = False
        IPublish(audio).retract(background=False)
        log.info('Podcast Episode %s successfully retracted.', audio.uniqueId)

    def _delete(self, audio):
        self._retract(audio)
        unique_id = audio.uniqueId
        del audio.__parent__[audio.__name__]
        self.__parent__ = None
        log.info('Podcast Episode %s successfully deleted.', unique_id)
