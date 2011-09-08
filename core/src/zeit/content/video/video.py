# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.dav
import zeit.cms.content.metadata
import zeit.cms.interfaces
import zeit.content.video.interfaces
import zope.interface


class Video(zeit.cms.content.metadata.CommonMetadata):

    zope.interface.implements(zeit.content.video.interfaces.IVideo)

    default_template = '<video></video>'

    zeit.cms.content.dav.mapProperties(
        zeit.content.video.interfaces.IVideo,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('has_recensions', 'expires', 'video_still', 'flv_url', 'thumbnail'))


class VideoType(zeit.cms.type.XMLContentTypeDeclaration):

    title = _('Video')
    interface = zeit.content.video.interfaces.IVideo
    addform = zeit.cms.type.SKIP_ADD
    factory = Video
    type = 'video'
