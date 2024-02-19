from datetime import datetime
from typing import Optional
import logging

import pytz
import zope.app.appsetup.product
import zope.component
import zope.interface

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import IUUID, ISemanticChange
from zeit.cms.repository.interfaces import IFolder
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
from zeit.connector.search import SearchVar
from zeit.content.article.interfaces import IArticle
from zeit.content.audio.audio import AUDIO_SCHEMA_NS, Audio
from zeit.content.audio.interfaces import IAudio, IAudioReferences, ISpeechInfo
from zeit.speech.errors import AudioReferenceError
import zeit.cms.interfaces
import zeit.cms.repository.folder
import zeit.speech.interfaces


log = logging.getLogger(__name__)

AUDIO_ID = SearchVar('article_uuid', AUDIO_SCHEMA_NS)


@zope.interface.implementer(zeit.speech.interfaces.ISpeech)
class Speech:
    def __init__(self):
        self.config = zope.app.appsetup.product.getProductConfiguration('zeit.speech')

    def _get_target_folder(self, article_uuid: str) -> IFolder:
        """Returns the folder corresponding to the article's first release date."""
        repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        speech_folder = self.config['speech-folder']

        article = zeit.cms.interfaces.ICMSContent(IUUID(article_uuid))
        yyyy_mm = IPublishInfo(article).date_first_released.strftime('%Y-%m')
        if speech_folder not in repository:
            repository[speech_folder] = zeit.cms.repository.folder.Folder()
        if yyyy_mm not in repository[speech_folder]:
            repository[speech_folder][yyyy_mm] = zeit.cms.repository.folder.Folder()
        return repository[speech_folder][yyyy_mm]

    @staticmethod
    def convert_ms_to_sec(milliseconds: int) -> int:
        # XXX no need for try once we have openapi validation
        try:
            return int(milliseconds / 1000)
        except TypeError:
            return 0

    def _create(self, data: dict) -> IAudio:
        speech = Audio()
        speech.audio_type = 'tts'
        folder = self._get_target_folder(data['uuid'])
        folder[data['uuid']] = speech
        log.info('Created %s for article uuid %s', speech, data['uuid'])
        self._update(data, folder[data['uuid']])
        return folder[data['uuid']]

    def _update(self, data: dict, speech: IAudio):
        with checked_out(speech) as co:
            for audio in data['articlesAudio']:
                audio_entry = audio['audioEntry']
                if audio['type'] == 'FULL_TTS':
                    co.url = audio_entry['url']
                    co.duration = self.convert_ms_to_sec(audio_entry.get('duration'))
                    ISpeechInfo(co).article_uuid = data['uuid']
                    ISpeechInfo(co).checksum = audio.get('checksum')
                elif audio['type'] == 'PREVIEW_TTS':
                    ISpeechInfo(co).preview_url = audio_entry['url']
            ISemanticChange(co).last_semantic_change = datetime.now(pytz.UTC)
        log.info('Updated %s for article uuid %s', speech, data['uuid'])

    def _find(self, article_uuid: str) -> Optional[IAudio]:
        connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
        result = list(connector.search([AUDIO_ID], (AUDIO_ID == str(article_uuid))))
        if not result:
            return None
        content = zeit.cms.interfaces.ICMSContent(result[0][0])
        log.debug('%s found for article uuid %s.', content, article_uuid)
        return content

    def update(self, data: dict):
        article_uuid = data['uuid']
        speech = self._find(article_uuid)
        if speech:
            self._update(data, speech)
        else:
            speech = self._create(data)
        self._add_audio_reference(speech)

    def _add_audio_reference(self, speech: IAudio):
        article = self._assert_article_unchanged(speech)

        IPublish(speech).publish(background=False)
        if speech in IAudioReferences(article).items:
            log.debug('%s already references %s', article, speech)
            return
        with checked_out(article, raise_if_error=True) as co:
            references = IAudioReferences(co)
            references.add(speech)
        log.info('Added reference from %s to %s', article, speech)
        IPublish(article).publish(background=False)

    def _article(self, speech: IAudio) -> IArticle:
        return zeit.cms.interfaces.ICMSContent(
            zeit.cms.content.interfaces.IUUID(ISpeechInfo(speech).article_uuid), None
        )

    def _assert_article_unchanged(self, speech: IAudio) -> IArticle:
        article = self._article(speech)
        last_modified = zeit.cms.workflow.interfaces.IModified(article).date_last_modified
        last_published = zeit.cms.workflow.interfaces.IPublishInfo(article).date_last_published
        if last_modified > last_published:
            raise AudioReferenceError(
                '%s was modified after publish. Skipped adding reference %s.',
                article,
                speech,
            )
        return article

    def _remove_reference_from_article(self, speech: IAudio):
        article = self._article(speech)
        if not article:
            log.warning(
                'No article found for %s. Maybe it was already deleted?',
                speech,
            )
            return
        with checked_out(article, raise_if_error=True) as co:
            references = IAudioReferences(co)
            references.items = tuple(ref for ref in references.items if ref != speech)

    def delete(self, data: dict):
        speech = self._find(data['article_uuid'])
        if not speech:
            log.warning(
                'No audio object found for article uuid %s. '
                'Maybe it was already deleted?' % data['article_uuid'],
            )
            return
        self._remove_reference_from_article(speech)
        IPublish(speech).retract(background=False)
        unique_id = speech.uniqueId
        del speech.__parent__[speech.__name__]
        log.info('Deleted %s', unique_id)
