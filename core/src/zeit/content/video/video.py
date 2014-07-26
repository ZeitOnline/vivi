# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import grokcore.component
import lxml.objectify
import pkg_resources
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.video.interfaces
import zeit.workflow.interfaces
import zope.interface


class RenditionsProperty(zeit.cms.content.property.MultiPropertyBase):

    def _element_factory(self, node, tree):
        result = VideoRendition()
        result.url = node.get('url')
        result.frame_width = int(node.get('frame_width'))
        return result

    def _node_factory(self, entry, tree):
        node = lxml.objectify.E.rendition()
        node.set('url', entry.url)
        node.set('frame_width', str(entry.frame_width))
        return node


class Video(zeit.cms.content.metadata.CommonMetadata):

    zope.interface.implements(zeit.content.video.interfaces.IVideo,
                              zeit.cms.interfaces.IAsset)

    default_template = pkg_resources.resource_string(__name__,
                                                     'video-template.xml')

    zeit.cms.content.dav.mapProperties(
        zeit.content.video.interfaces.IVideo,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('has_recensions', 'expires', 'video_still', 'flv_url', 'thumbnail'))

    id_prefix = 'vid'

    # Note: zeit.brightcove will inject a brightcove_id property here in order
    # to avoid a package dependency of zeit.content.video on the interface to
    # a particular external video service.

    @property
    def teaserTitle(self):
        return self.title

    renditions = RenditionsProperty('.head.renditions.rendition')


class VideoRendition():
    zope.interface.implements(zeit.content.video.interfaces.IVideoRendition)
    frame_width = 0
    url = None


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

    def update(self, node):
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
        return relations.get_relations(self.context)
