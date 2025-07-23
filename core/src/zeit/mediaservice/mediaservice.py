import zeit.cms.celery
import zeit.cms.interfaces


@zeit.cms.celery.task(queue='mediaservice')
def create_audio_objects(volume_uniqueid):
    volume = zeit.cms.interfaces.ICMSContent(volume_uniqueid)
    volume.ensure_audio_folder()
    articles = volume.get_articles()
    audios = volume.get_audios()
    volume.create_audio_objects(articles, audios)
