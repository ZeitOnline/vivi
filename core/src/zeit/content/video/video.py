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
import zeit.content.video.interfaces
import zope.interface


class EmptyStringStructure(zeit.cms.content.property.Structure):

    # XXX Should this behaviour be built into the super-class? (re #9833)

    def __set__(self, instance, value):
        if value is None:
            value = ''
        super(EmptyStringStructure, self).__set__(instance, value)


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

    subtitle = EmptyStringStructure(
        '.body.subtitle',
        zeit.cms.content.interfaces.ICommonMetadata['subtitle'])


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
        image_node = node.find('image')
        if image_node is not None:
            node.remove(image_node)
        if self.context.video_still:
            node.append(lxml.objectify.E.image(
                src=self.context.video_still))

        thumbnail_node = node.find('thumbnail')
        if thumbnail_node is not None:
            node.remove(thumbnail_node)
        if self.context.thumbnail:
            node.append(lxml.objectify.E.thumbnail(
                src=self.context.thumbnail))

        node.set('type', 'video')
