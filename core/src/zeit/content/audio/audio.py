from zeit.cms.i18n import MessageFactory as _
import zope.interface
import zope.component
import zeit.cms.interfaces
import zeit.cms.content.dav
import zeit.cms.content.xmlsupport
import zeit.cms.repository.interfaces
import zeit.cms.repository.folder
import zeit.cms.type
import zeit.content.audio.interfaces


@zope.interface.implementer(
    zeit.content.audio.interfaces.IAudio,
    zeit.cms.interfaces.IAsset)
class Audio(zeit.cms.content.xmlsupport.XMLContentBase):
    default_template = '<audio><head/><body/></audio>'

    title = zeit.cms.content.dav.DAVProperty(
        zeit.content.audio.interfaces.IAudio['title'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'title')

    episodeId = zeit.cms.content.dav.DAVProperty(
        zeit.content.audio.interfaces.IAudio['episodeId'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'episode_id')

    url = zeit.cms.content.dav.DAVProperty(
        zeit.content.audio.interfaces.IAudio['url'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'url')

    def update(self, info):
        self.title = info['title']
        self.url = info['audio_file_url']


def audio_container(create=False):
    container_id = 'audio'
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    if container_id in repository:
        return repository[container_id]
    if create:
        repository[container_id] = zeit.cms.repository.folder.Folder()
        return repository[container_id]


def add_audio(container, info):
    audio = Audio()
    audio.episodeId = info['id']
    audio.update(info)
    container[info['id']] = audio
    return audio


def remove_audio(context):
    del context.__parent__[context.__name__]
    context.__parent__ = None
    return context


class AudioType(zeit.cms.type.XMLContentTypeDeclaration):
    factory = Audio
    interface = zeit.content.audio.interfaces.IAudio
    title = _('Audio')
    type = 'audio'  # Wert für {http://namespaces.zeit.de/CMS/meta}type
