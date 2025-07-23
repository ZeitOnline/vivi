import zeit.cms.celery
import zeit.cms.interfaces


@zeit.cms.celery.task(queue='mediaservice')
def create_audio_objects(volume_uniqueid):
    volume = zeit.cms.interfaces.ICMSContent(volume_uniqueid)
    volume.process_audios()
    pass
