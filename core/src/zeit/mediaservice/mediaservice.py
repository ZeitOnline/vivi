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
                # AudioReferences deduplicates through zeit.cms.content.reference.ReferenceProperty
                references.add(folder[article_uuid.shortened])

    def create_audio_object(self, mediasync_id, audio_info):
        audio = zeit.content.audio.audio.Audio()
        audio.audio_type = 'premium'
        audio.external_id = mediasync_id
        audio.url = audio_info['url']
        audio.duration = audio_info['duration']
        return audio
