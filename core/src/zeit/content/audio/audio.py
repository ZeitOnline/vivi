import logging

import grokcore.component as grok
import zope.component
import zope.interface

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.interfaces import AUDIO_SCHEMA_NS
from zeit.content.audio.interfaces import IAudio, IPodcastEpisodeInfo, ISpeechInfo
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.interfaces
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.cms.type
import zeit.content.article.interfaces
import zeit.content.audio.interfaces
import zeit.content.image.interfaces


log = logging.getLogger(__name__)


@zope.interface.implementer(IAudio, zeit.cms.interfaces.IAsset)
class Audio(zeit.cms.content.metadata.CommonMetadata):
    default_template = '<audio><head/><body/></audio>'

    zeit.cms.content.dav.mapProperties(
        zeit.content.audio.interfaces.IAudio,
        AUDIO_SCHEMA_NS,
        ('external_id', 'url', 'duration', 'audio_type'),
    )

    @property
    def teaserTitle(self):  # @@object-details expects this
        return self.title


@zope.interface.implementer(IPodcastEpisodeInfo)
class PodcastEpisodeInfo(zeit.cms.content.dav.DAVPropertiesAdapter):
    grok.context(IAudio)

    zeit.cms.content.dav.mapProperties(
        IPodcastEpisodeInfo,
        AUDIO_SCHEMA_NS,
        (
            'podcast',
            'podcast_id',
            'episode_nr',
            'url_ad_free',
            'is_published',
            'dashboard_link',
        ),
    )

    summary = zeit.cms.content.property.ObjectPathProperty(
        '.summary', IPodcastEpisodeInfo['summary']
    )
    notes = zeit.cms.content.property.ObjectPathProperty('.notes', IPodcastEpisodeInfo['notes'])

    def __init__(self, context):
        self.xml = context.xml
        self.context = context


class AudioType(zeit.cms.type.XMLContentTypeDeclaration):
    factory = Audio
    interface = IAudio
    title = _('Audio')
    type = 'audio'  # Wert für {http://namespaces.zeit.de/CMS/meta}type


@grok.implementer(zeit.content.image.interfaces.IImages)
class PodcastImage(grok.Adapter):
    grok.context(IAudio)

    def _get_podcast(self):
        if self.context.audio_type == 'podcast':
            info = IPodcastEpisodeInfo(self.context)
            return info.podcast

    @property
    def fill_color(self):
        podcast = self._get_podcast()
        if podcast:
            return podcast.color

    @property
    def image(self):
        podcast = self._get_podcast()
        if podcast and podcast.image:
            return zeit.cms.interfaces.ICMSContent(podcast.image, None)


@grok.implementer(ISpeechInfo)
class SpeechInfo(zeit.cms.content.dav.DAVPropertiesAdapter):
    grok.context(IAudio)
    zeit.cms.content.dav.mapProperties(
        ISpeechInfo, AUDIO_SCHEMA_NS, ('article_uuid', 'preview_url', 'checksum')
    )
