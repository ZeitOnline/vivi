import opentelemetry.trace
import zope.component

from zeit.cms.checkout.helper import checked_out
from zeit.connector.search import SearchVar
import zeit.cms.celery
import zeit.cms.content.add
import zeit.cms.interfaces
import zeit.content.audio.audio


MEDIASYNC_ID = SearchVar('mediasync_id', zeit.cms.interfaces.IR_NAMESPACE)


@zeit.cms.celery.task(queue='mediaservice')
def create_audio_objects(volume_uniqueid):
    volume = zeit.cms.interfaces.ICMSContent(volume_uniqueid)
    mediaservice = MediaService()
    mediaservice.create_audio_objects(volume)


class MediaService:
    def create_audio_objects(self, volume):
        folder = self._audio_folder(volume)
        audios = self._get_audios(volume)
        self._create_audio_objects(folder, audios)

    def _get_audios(self, volume):
        connection = zope.component.getUtility(zeit.mediaservice.interfaces.IConnection)
        return connection.get_audio_infos(volume.year, volume.volume)

    def _audio_folder(self, volume):
        return zeit.cms.content.add.find_or_create_folder(
            'premium', 'audio', str(volume.year), volume.volume_number
        )

    def _get_article(self, mediasync_id):
        connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
        result = list(connector.search([MEDIASYNC_ID], (MEDIASYNC_ID == str(mediasync_id))))
        if not result:
            return None
        return zeit.cms.interfaces.ICMSContent(result[0][0])

    def _create_audio_objects(self, folder, audios):
        for mediasync_id, audio_info in audios.items():
            article = self._get_article(mediasync_id)
            if not article:
                err = ValueError(
                    f'No article with {mediasync_id} found for available premium audio'
                )
                current_span = opentelemetry.trace.get_current_span()
                current_span.record_exception(err)
                continue

            audio = self.create_audio_object(mediasync_id, audio_info)
            if not audio:
                continue

            article_uuid = zeit.cms.content.interfaces.IUUID(article)
            folder[article_uuid.shortened] = audio
            with checked_out(article, raise_if_error=True) as co:
                co.has_audio = True
                references = zeit.content.audio.interfaces.IAudioReferences(co)
                # AudioReferences deduplicates through zeit.cms.content.reference.ReferenceProperty
                references.add(folder[article_uuid.shortened])

    def create_audio_object(self, mediasync_id, audio_info):
        audio = zeit.content.audio.audio.Audio()
        audio.audio_type = 'premium'
        audio.external_id = mediasync_id
        audio.url = audio_info['url']
        audio.duration = audio_info['duration']
        return audio
