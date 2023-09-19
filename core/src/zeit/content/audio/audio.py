from zeit.cms.i18n import MessageFactory as _
from zeit.content.audio.interfaces import IAudio, IPodcastEpisodeInfo

import logging

import grokcore.component as grok
import zope.component
import zope.interface

import zeit.cms.content.dav
import zeit.cms.content.property
import zeit.cms.content.interfaces
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.cms.type
import zeit.content.audio.interfaces


log = logging.getLogger(__name__)

AUDIO_SCHEMA_NS = 'http://namespaces.zeit.de/CMS/audio'


@zope.interface.implementer(
    IAudio,
    zeit.cms.interfaces.IAsset)
class Audio(zeit.cms.content.xmlsupport.XMLContentBase):
    default_template = '<audio><head/><body/></audio>'

    zeit.cms.content.dav.mapProperties(
        zeit.content.audio.interfaces.IAudio,
        AUDIO_SCHEMA_NS, (
            'external_id',
            'title',
            'url',
            'duration',
            'audio_type'))

    def __getattr__(self, name):
        if name in zeit.cms.content.interfaces.ICommonMetadata:
            return zeit.cms.content.interfaces.ICommonMetadata[name].default
        raise AttributeError(name)

@zope.interface.implementer(IPodcastEpisodeInfo)
class PodcastEpisodeInfo(zeit.cms.content.dav.DAVPropertiesAdapter):

    grok.context(IAudio)

    zeit.cms.content.dav.mapProperties(
        IPodcastEpisodeInfo,
        AUDIO_SCHEMA_NS, (
            'podcast',
            'image',
            'episode_nr'))

    summary = zeit.cms.content.property.ObjectPathProperty(
        '.summary', IPodcastEpisodeInfo['summary'])
    notes = zeit.cms.content.property.ObjectPathProperty(
        '.notes', IPodcastEpisodeInfo['notes'])

    def __init__(self, context):
        self.xml = context.xml
        self.context = context


class AudioType(zeit.cms.type.XMLContentTypeDeclaration):
    factory = Audio
    interface = IAudio
    title = _('Audio')
    type = 'audio'  # Wert für {http://namespaces.zeit.de/CMS/meta}type
