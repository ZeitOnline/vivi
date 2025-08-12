import opentelemetry.trace
import pendulum
import zope.component

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import ISemanticChange
from zeit.cms.i18n import MessageFactory as _
from zeit.connector.search import SearchVar
from zeit.content.audio.interfaces import IAudioReferences
import zeit.cms.celery
import zeit.cms.content.add
import zeit.cms.interfaces
import zeit.content.audio.audio
import zeit.objectlog.interfaces


MEDIASYNC_ID = SearchVar('mediasync_id', zeit.cms.interfaces.IR_NAMESPACE)


@zeit.cms.celery.task(queue='mediaservice')
def create_audio_objects(volume_uniqueid):
    volume = zeit.cms.interfaces.ICMSContent(volume_uniqueid)
    mediaservice = MediaService()
    articles = mediaservice.create_audio_objects(volume)
    log = zeit.objectlog.interfaces.ILog(volume)
    log.log(
        _(
            'Found ${existing} and created ${created} premium audio objects',
            mapping={'existing': articles['existing_count'], 'created': len(articles['created'])},
        )
    )
    if articles['created']:
        log.log(
            _(
                'Audio objects created for the following articles: ${articles}',
                mapping={'articles': ', '.join(articles['created'])},
            )
        )


class MediaService:
    def create_audio_objects(self, volume):
        folder = self._audio_folder(volume)
        audios = self._get_audios(volume)
        return self._create_audio_objects(folder, audios)

    def _get_audios(self, volume):
        connection = zope.component.getUtility(zeit.mediaservice.interfaces.IConnection)
        return connection.get_audio_infos(volume.year, volume.volume)

    def _audio_folder(self, volume):
        return zeit.cms.content.add.find_or_create_folder(
            'premium', 'audio', str(volume.year), volume.volume_number
        )

    def _get_articles(self, mediasync_id):
        connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
        result = list(connector.search([MEDIASYNC_ID], (MEDIASYNC_ID == str(mediasync_id))))
        if not result:
            return None
        return (zeit.cms.interfaces.ICMSContent(i[0]) for i in result)

    def _create_audio_objects(self, folder, audios):
        articles_created = set()
        articles_existing = set()
        for mediasync_id, audio_info in audios.items():
            articles = self._get_articles(mediasync_id)
            if not articles:
                err = ValueError(
                    f'No article with mediasync id {mediasync_id} found for available premium audio'
                )
                current_span = opentelemetry.trace.get_current_span()
                current_span.record_exception(err)
                continue

            for article in articles:
                article_uuid = zeit.cms.content.interfaces.IUUID(article)
                if article_uuid.shortened not in folder:
                    articles_created.add(article.uniqueId)
                    audio = self.create_audio_object(mediasync_id, audio_info)
                    audio.title = article.title
                    folder[article_uuid.shortened] = audio
                else:
                    articles_existing.add(article.uniqueId)

                if not IAudioReferences(article).get_by_type('premium'):
                    with checked_out(article, raise_if_error=True) as co:
                        references = IAudioReferences(co)
                        references.add(folder[article_uuid.shortened])
        return {'created': sorted(articles_created), 'existing_count': len(articles_existing)}

    def create_audio_object(self, mediasync_id, audio_info):
        audio = zeit.content.audio.audio.Audio()
        audio.audio_type = 'premium'
        audio.external_id = mediasync_id
        audio.url = audio_info['url']
        audio.duration = audio_info['duration']
        ISemanticChange(audio).last_semantic_change = pendulum.now('UTC')
        return audio
