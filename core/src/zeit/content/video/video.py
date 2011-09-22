# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import pkg_resources
import zeit.cms.content.dav
import zeit.cms.content.metadata
import zeit.cms.interfaces
import zeit.content.video.interfaces
import zope.interface


class Video(zeit.cms.content.metadata.CommonMetadata):

    zope.interface.implements(zeit.content.video.interfaces.IVideo,
                              zeit.cms.interfaces.IAsset)

    default_template = pkg_resources.resource_string(__name__,
                                                     'video-template.xml')

    zeit.cms.content.dav.mapProperties(
        zeit.content.video.interfaces.IVideo,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('has_recensions', 'expires', 'video_still', 'flv_url', 'thumbnail'))

    # Note: zeit.brightcove will inject a brightcove_id property here in order
    # to avoid a package dependency of zeit.content.video on the interface to
    # a particular external video service.


class VideoType(zeit.cms.type.XMLContentTypeDeclaration):

    title = _('Video')
    interface = zeit.content.video.interfaces.IVideo
    addform = zeit.cms.type.SKIP_ADD
    factory = Video
    type = 'video'
