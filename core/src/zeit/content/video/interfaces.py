# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zope.schema
import zeit.cms.content.interfaces
import zeit.cms.interfaces


class IVideo(zeit.cms.content.interfaces.ICommonMetadata,
             zeit.cms.interfaces.ICMSContent):

    has_recensions = zope.schema.Bool(
        title=_('Has recension content'),
        default=False)

    expires = zope.schema.Datetime(
        title=_('Video expires on'),
        required=False,
        readonly=True,
        default=None)

    video_still = zope.schema.URI(
        title=_('URI of the still image'),
        required=False,
        readonly=True)

    flv_url = zope.schema.URI(
        title=_('URI of the video file'),
        required=False,
        readonly=True)

    thumbnail = zope.schema.URI(
        title=_('URI of the thumbnail'),
        required=False,
        readonly=True)


class IPlaylist(zeit.cms.content.interfaces.ICommonMetadata,
                zeit.cms.interfaces.ICMSContent):

    video_ids = zope.schema.Tuple(
        title=_("Video IDs"),
        required=False,
        default=(),
        unique=False,
        value_type=zope.schema.URI(
            title=_('URI of the Playlist-Video'),
            required=False,
            readonly=True)
    )
