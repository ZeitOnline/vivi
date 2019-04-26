from zeit.cms.i18n import MessageFactory as _
from zope.cachedescriptors.property import Lazy as cachedproperty
import grokcore.component as grok
import lxml.objectify
import pkg_resources
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zeit.cms.content.reference
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.video.interfaces
import zeit.push.interfaces
import zeit.workflow.dependency
import zope.interface


class AuthorshipsProperty(zeit.cms.content.reference.ReferenceProperty):
    """Drop-in ReferenceProperty that also accepts plain ICMSContent on set.

    Since one cannot enter location information in Brightcove, authors of
    videos can never have that, so we don't need to care about it (and can make
    life simpler for zeit.brightcove).
    """

    # Similar to zeit.cms.content.reference.MultiResource, but only the setter.

    def references(self, instance):
        """Returns a ``References`` object to easen creation of references."""
        return super(AuthorshipsProperty, self).__get__(instance, None)

    def __set__(self, instance, value):
        items = []
        references = self.references(instance)
        for item in value:
            if zeit.cms.content.interfaces.IReference.providedBy(item):
                items.append(item)
            else:
                items.append(references.create(item))
        super(AuthorshipsProperty, self).__set__(instance, items)


class Video(zeit.cms.content.metadata.CommonMetadata):

    zope.interface.implements(zeit.content.video.interfaces.IVideo,
                              zeit.cms.interfaces.IAsset)

    default_template = pkg_resources.resource_string(__name__,
                                                     'video-template.xml')

    zeit.cms.content.dav.mapProperties(
        zeit.content.video.interfaces.IVideo,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('has_recensions', 'expires', 'video_still_copyright'))

    zeit.cms.content.dav.mapProperties(
        zeit.content.video.interfaces.IVideo,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('has_advertisement',), use_default=True)

    id_prefix = 'vid'

    external_id = zeit.cms.content.dav.DAVProperty(
        zeit.content.video.interfaces.IVideo['external_id'],
        # BBB This field used to be injected into here from zeit.brightcove
        'http://namespaces.zeit.de/CMS/brightcove', 'id')

    @property
    def renditions(self):
        return self._player_data['renditions']

    @property
    def highest_rendition_url(self):
        if not self.renditions:
            return None
        high = sorted(self.renditions, key=lambda r: r.frame_width).pop()
        return getattr(high, 'url', '')

    @property
    def thumbnail(self):
        return self._player_data['thumbnail']

    @property
    def video_still(self):
        return self._player_data['video_still']

    @cachedproperty
    def _player_data(self):
        player = zope.component.getUtility(
            zeit.content.video.interfaces.IPlayer)
        return player.get_video(self.external_id)

    @property
    def teaserTitle(self):
        return self.title

    authorships = AuthorshipsProperty(
        str(zeit.cms.content.metadata.CommonMetadata.authorships.path),
        zeit.cms.content.metadata.CommonMetadata.authorships.xml_reference_name
    )

    # Override from CommonMetadata to change the source
    serie = zeit.cms.content.dav.DAVProperty(
        zeit.content.video.interfaces.IVideo['serie'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'serie')

    @property
    def seo_slug(self):
        titles = (t for t in (self.supertitle, self.title) if t)
        return zeit.cms.interfaces.normalize_filename(u' '.join(titles))


class VideoRendition():
    zope.interface.implements(zeit.content.video.interfaces.IVideoRendition)
    frame_width = 0
    url = None
    video_duration = 0


class VideoType(zeit.cms.type.XMLContentTypeDeclaration):

    title = _('Video')
    interface = zeit.content.video.interfaces.IVideo
    addform = zeit.cms.type.SKIP_ADD
    factory = Video
    type = 'video'


class VideoXMLReferenceUpdater(grok.Adapter):

    grok.context(zeit.content.video.interfaces.IVideo)
    grok.name('brightcove-image')
    grok.implements(zeit.cms.content.interfaces.IXMLReferenceUpdater)

    def update(self, node, suppress_errors=False):
        still_node = node.find('video-still')
        if still_node is not None:
            node.remove(still_node)
        if self.context.video_still:
            node.append(getattr(lxml.objectify.E, 'video-still')(
                src=self.context.video_still))

        thumbnail_node = node.find('thumbnail')
        if thumbnail_node is not None:
            node.remove(thumbnail_node)
        if self.context.thumbnail:
            node.append(lxml.objectify.E.thumbnail(
                src=self.context.thumbnail))

        node.set('type', 'video')


class Dependencies(zeit.workflow.dependency.DependencyBase):

    grok.context(zeit.content.video.interfaces.IVideo)
    grok.name('zeit.content.video')

    def get_dependencies(self):
        relations = zope.component.getUtility(
            zeit.cms.relation.interfaces.IRelations)
        return [x for x in relations.get_relations(self.context)
                if zeit.content.video.interfaces.IPlaylist.providedBy(x)]


@grok.adapter(zeit.content.video.interfaces.IVideo)
@grok.implementer(zeit.push.interfaces.IPushURL)
def video_push_url(context):
    return context.uniqueId + '/' + context.seo_slug
