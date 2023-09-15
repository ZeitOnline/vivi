from zeit.cms.i18n import MessageFactory as _
import logging
import zope.interface
import zope.component
import zeit.cms.interfaces
import zeit.cms.content.dav
import zeit.cms.content.xmlsupport
import zeit.cms.repository.interfaces
import zeit.cms.repository.folder
import zeit.cms.type
import zeit.content.audio.interfaces


log = logging.getLogger(__name__)

AUDIO_SCHEMA_NS = 'http://namespaces.zeit.de/CMS/audio'


@zope.interface.implementer(
    zeit.content.audio.interfaces.IAudio,
    zeit.cms.interfaces.IAsset)
class Audio(zeit.cms.content.xmlsupport.XMLContentBase):
    default_template = '<audio><head/><body/></audio>'

    zeit.cms.content.dav.mapProperties(
        zeit.content.audio.interfaces.IAudio,
        AUDIO_SCHEMA_NS, (
            'title',
            'image',
            'episode_id',
            'episode_nr',
            'url',
            'duration',
            'description',
            # XXX Very temporary fix until we add podcast series object
            'serie',
            'serie_subtitle',
            'distribution_channels'))

    def update(self, info):
        self.title = info['title']
        self.url = info['audio_file_url']


def add_audio(container, info):
    log.info('Add audio %s', info['id'])
    audio = Audio()
    audio.episode_id = info['id']
    audio.update(info)
    container[info['id']] = audio
    return audio


def remove_audio(context):
    log.info('Remove audio %s', context.__name__)
    del context.__parent__[context.__name__]
    context.__parent__ = None
    return context


class AudioType(zeit.cms.type.XMLContentTypeDeclaration):
    factory = Audio
    interface = zeit.content.audio.interfaces.IAudio
    title = _('Audio')
    type = 'audio'  # Wert für {http://namespaces.zeit.de/CMS/meta}type
