from zope.cachedescriptors.property import Lazy as cachedproperty
import grokcore.component as grok
import zope.interface

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zeit.cms.content.reference
import zeit.cms.interfaces
import zeit.cms.related.related
import zeit.cms.type
import zeit.cms.workflow.dependency
import zeit.content.video.interfaces
import zeit.push.interfaces


class AuthorshipsProperty(zeit.cms.content.reference.ReferenceProperty):
    """Drop-in ReferenceProperty that also accepts plain ICMSContent on set.

    Since one cannot enter location information in Brightcove, authors of
    videos can never have that, so we don't need to care about it (and can make
    life simpler for zeit.brightcove).
    """

    # Similar to zeit.cms.content.reference.MultiResource, but only the setter.

    def references(self, instance):
        """Returns a ``References`` object to easen creation of references."""
        return super().__get__(instance, None)

    def __set__(self, instance, value):
        items = []
        references = self.references(instance)
        for item in value:
            if zeit.cms.content.interfaces.IReference.providedBy(item):
                items.append(item)
            else:
                items.append(references.create(item))
        super().__set__(instance, items)


@zope.interface.implementer(zeit.content.video.interfaces.IVideo, zeit.cms.interfaces.IAsset)
class Video(zeit.cms.content.metadata.CommonMetadata):
    default_template = """\
<video>
    <head/>
    <body/>
</video>"""

    external_id = zeit.cms.content.dav.DAVProperty(
        zeit.content.video.interfaces.IVideo['external_id'],
        # BBB This field used to be injected into here from zeit.brightcove
        'http://namespaces.zeit.de/CMS/brightcove',
        'id',
    )

    type = zeit.cms.content.dav.DAVProperty(
        zeit.content.video.interfaces.IVideo['type'],
        'http://namespaces.zeit.de/CMS/video',
        'type',
        use_default=True,
    )

    zeit.cms.content.dav.mapProperties(
        zeit.content.video.interfaces.IVideo,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('expires', 'video_still_copyright'),
    )

    zeit.cms.content.dav.mapProperties(
        zeit.content.video.interfaces.IVideo,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('has_advertisement',),
        use_default=True,
    )

    kind = zeit.cms.content.dav.DAVProperty(
        zeit.content.video.interfaces.IVideo['kind'], 'http://namespaces.zeit.de/CMS/video', 'kind'
    )

    zeit.cms.content.dav.mapProperties(
        zeit.content.video.interfaces.IVideo,
        'http://namespaces.zeit.de/CMS/video',
        ('duration', 'width', 'url'),
    )

    body = zeit.cms.content.property.Structure('.body.text')

    @property
    def renditions(self):
        return self._player_data['renditions']

    @property
    def highest_rendition_url(self):
        if not self.renditions:
            return None
        high = sorted(self.renditions, key=lambda r: r.frame_width).pop()
        return getattr(high, 'url', '')

    @cachedproperty
    def _player_data(self):
        # XXX Kludgy temporary workaround until we integrate with Youtube API.
        if self.video_type == 'youtube':
            rendition = VideoRendition()
            rendition.url = self.url
            rendition.frame_width = self.width
            rendition.video_duration = self.duration
            return {'renditions': [rendition]}
        player = zope.component.getUtility(zeit.content.video.interfaces.IPlayer)
        return player.get_video(self.external_id)

    @property
    def teaserTitle(self):
        return self.title

    authorships = AuthorshipsProperty(
        str(zeit.cms.content.metadata.CommonMetadata.authorships.path),
        zeit.cms.content.metadata.CommonMetadata.authorships.xml_reference_name,
    )

    # Override from CommonMetadata to change the source
    serie = zeit.cms.content.dav.DAVProperty(
        zeit.content.video.interfaces.IVideo['serie'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'serie',
    )

    @property
    def seo_slug(self):
        titles = (t for t in (self.supertitle, self.title) if t)
        return zeit.cms.interfaces.normalize_filename(' '.join(titles))

    @property
    def live_url_base(self):
        return f'{self.uniqueId}/{self.seo_slug}'


@zope.component.adapter(zeit.content.video.interfaces.IVideo)
@zope.interface.implementer(zeit.content.image.interfaces.IImages)
class VideoImage(zeit.cms.related.related.RelatedBase):
    image = zeit.cms.content.reference.SingleResource('.body.video_still', 'image')

    fill_color = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.body.video_still', 'fill_color', zeit.content.image.interfaces.IImages['fill_color']
    )


@zope.interface.implementer(zeit.content.video.interfaces.IVideoRendition)
class VideoRendition:
    frame_width = 0
    url = None
    video_duration = 0


class VideoType(zeit.cms.type.XMLContentTypeDeclaration):
    title = _('Video')
    interface = zeit.content.video.interfaces.IVideo
    addform = zeit.cms.type.SKIP_ADD
    factory = Video
    type = 'video'


class DependenciesImages(zeit.cms.workflow.dependency.DependencyBase):
    grok.context(zeit.content.video.interfaces.IVideo)
    grok.name('zeit.content.video.still')

    retract_dependencies = True

    def get_dependencies(self):
        img = zeit.content.image.interfaces.IImages(self.context)
        if img.image is not None:
            return [img.image]
        else:
            return []


@grok.adapter(zeit.content.video.interfaces.IVideo)
@grok.implementer(zeit.push.interfaces.IPushURL)
def video_push_url(context):
    return context.live_url_base
