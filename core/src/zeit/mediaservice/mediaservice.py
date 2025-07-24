import opentelemetry.trace
import zope.component

from zeit.cms.checkout.helper import checked_out
import zeit.cms.celery
import zeit.cms.content.add
import zeit.cms.interfaces
import zeit.content.audio.audio


@zeit.cms.celery.task(queue='mediaservice')
def create_audio_objects(volume_uniqueid):
    volume = zeit.cms.interfaces.ICMSContent(volume_uniqueid)
    mediaservice = MediaService()
    mediaservice.create_audio_objects(volume)


class MediaService:
    def create_audio_objects(self, volume):
        articles = volume.get_articles()
        folder = self._audio_folder(volume)
        audios = self._get_audios(volume)
        self._create_audio_objects(folder, articles, audios)

    def _get_audios(self, volume):
        connection = zope.component.getUtility(zeit.mediaservice.interfaces.IConnection)
        return connection.get_audio_infos(volume.year, volume.volume)

    def _audio_folder(self, volume):
        return zeit.cms.content.add.find_or_create_folder(
            'premium', 'audio', str(volume.year), volume.volume_number
        )

    # FIXME: Peek at zeit.speech
    def _create_audio_objects(self, folder, articles, audios):
        for article in articles:
            audio_info = audios.get(article.ir_mediasync_id)
            if not audio_info:
                continue

            audio = self.create_audio_object(article.ir_mediasync_id, audio_info)
            if not audio:
                continue

            article_uuid = zeit.cms.content.interfaces.IUUID(article)
            folder[article_uuid.shortened] = audio
            with checked_out(article, raise_if_error=True) as co:
                references = zeit.content.audio.interfaces.IAudioReferences(co)
                # FIXME: Deduplicate, see speech
                references.add(folder[article_uuid.shortened])

    def create_audio_object(self, mediasync_id, audio_info):
        audio_url = audio_info.get('url')
        if not audio_url:
            err = ValueError(f'Premium audio info without URL for {mediasync_id}')
            current_span = opentelemetry.trace.get_current_span()
            current_span.record_exception(err)
            return

        audio = zeit.content.audio.audio.Audio()
        audio.audio_type = 'premium'
        audio.external_id = mediasync_id
        audio.url = audio_url
        audio_duration = audio_info.get('duration')  # FIXME: Parse duration ISO 8601
        if not audio_duration:
            err = ValueError(f'Premium audio info without duration for {mediasync_id}')
            current_span = opentelemetry.trace.get_current_span()
            current_span.record_exception(err)
        audio.duration = audio_duration
        return audio
