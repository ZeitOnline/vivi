from zeit.cms.i18n import MessageFactory as _
import grokcore.component
import lxml.objectify
import pkg_resources
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.video.interfaces
import zeit.workflow.interfaces
import zope.interface


class RenditionsProperty(zeit.cms.content.property.MultiPropertyBase):

    def _element_factory(self, node, tree):
        result = VideoRendition()
        result.url = node.get('url')
        if node.get('frame_width'):
            result.frame_width = int(node.get('frame_width'))
        if node.get('video_duration'):
            result.video_duration = int(node.get('video_duration'))
        return result

    def _node_factory(self, entry, tree):
        node = lxml.objectify.E.rendition()
        node.set('url', entry.url)
        if getattr(entry, 'frame_width', None):
            node.set('frame_width', str(entry.frame_width))
        if getattr(entry, 'video_duration', None):
            node.set('video_duration', str(entry.video_duration))
        return node


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
        ('has_recensions', 'expires', 'video_still', 'flv_url', 'thumbnail',
         'video_still_copyright'))

    id_prefix = 'vid'

    # Note: zeit.brightcove will inject a brightcove_id property here in order
    # to avoid a package dependency of zeit.content.video on the interface to
    # a particular external video service.

    @property
    def teaserTitle(self):
        return self.title

    renditions = RenditionsProperty('.head.renditions.rendition')
    authorships = AuthorshipsProperty(
        str(zeit.cms.content.metadata.CommonMetadata.authorships.path),
        zeit.cms.content.metadata.CommonMetadata.authorships.xml_reference_name
    )

    # XXX ``serie`` is copy&paste from CommonMetadata since we need to change
    # the source (thus the interface), and once we override the property
    # getter, we don't seem to be able to access the setter in the superclass
    # anymore.

    @property
    def serie(self):
        source = zeit.content.video.interfaces.IVideo['serie'].source(self)
        return source.factory.values.get(self._serie)

    @serie.setter
    def serie(self, value):
        if value is not None:
            if self._serie != value.serienname:
                self._serie = value.serienname
        else:
            self._serie = None


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


class VideoXMLReferenceUpdater(grokcore.component.Adapter):

    grokcore.component.context(zeit.content.video.interfaces.IVideo)
    grokcore.component.name('brightcove-image')
    grokcore.component.implements(
        zeit.cms.content.interfaces.IXMLReferenceUpdater)

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


class Dependencies(grokcore.component.Adapter):

    grokcore.component.context(
        zeit.content.video.interfaces.IVideo)
    grokcore.component.name('zeit.content.video')
    grokcore.component.implements(
        zeit.workflow.interfaces.IPublicationDependencies)

    def __init__(self, context):
        self.context = context

    def get_dependencies(self):
        relations = zope.component.getUtility(
            zeit.cms.relation.interfaces.IRelations)
        return [x for x in relations.get_relations(self.context)
                if zeit.content.video.interfaces.IPlaylist.providedBy(x)]
