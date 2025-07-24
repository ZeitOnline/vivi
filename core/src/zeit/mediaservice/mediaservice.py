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
    articles = volume.get_articles()
    ensure_audio_folder(volume)
    audios = get_audios(volume)
    _create_audio_objects(volume, articles, audios)


def get_audios(volume):
    ms = zope.component.getUtility(zeit.mediaservice.interfaces.IMediaService)
    return ms.get_audios(volume.year, volume.volume)


def ensure_audio_folder(volume):
    zeit.cms.content.add.find_or_create_folder(
        'premium', 'audio', str(volume.year), volume.volume_number
    )


# FIXME: Peek at zeit.speech
def _create_audio_objects(volume, articles, audios):
    repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
    folder = repository['premium']['audio'][str(volume.year)][volume.volume_number]
    for article in articles:
        audio_info = audios.get(article.ir_mediasync_id)
        if not audio_info:
            continue

        audio_url = audio_info.get('url')
        if not audio_url:
            err = ValueError(f'Premium audio info without URL for {article.ir_mediasync_id}')
            current_span = opentelemetry.trace.get_current_span()
            current_span.record_exception(err)
            continue

        article_uuid = zeit.cms.content.interfaces.IUUID(article)
        audio = zeit.content.audio.audio.Audio()
        audio.audio_type = 'premium'
        audio.external_id = article.ir_mediasync_id
        audio.url = audio_url
        audio_duration = audio_info.get('duration')  # FIXME: Parse duration ISO 8601
        if not audio_duration:
            err = ValueError(f'Premium audio info without duration for {article.ir_mediasync_id}')
            current_span = opentelemetry.trace.get_current_span()
            current_span.record_exception(err)
        audio.duration = audio_duration

        folder[article_uuid.shortened] = audio
        with checked_out(article, raise_if_error=True) as co:
            references = zeit.content.audio.interfaces.IAudioReferences(co)
            # FIXME: Deduplicate, see speech
            references.add(folder[article_uuid.shortened])
