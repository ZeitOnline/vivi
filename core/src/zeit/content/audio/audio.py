from zeit.cms.i18n import MessageFactory as _
import zope.interface
import zeit.cms.interfaces
import zeit.cms.content.dav
import zeit.cms.content.xmlsupport
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


class AudioType(zeit.cms.type.XMLContentTypeDeclaration):
    factory = Audio
    interface = zeit.content.audio.interfaces.IAudio
    title = _('Audio')
    type = 'audio'  # Wert für {http://namespaces.zeit.de/CMS/meta}type
