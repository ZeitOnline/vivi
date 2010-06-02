# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import grokcore.component
import lxml.objectify
import pytz
import zeit.brightcove.interfaces
import zeit.cms.content.dav
import zeit.cms.interfaces
import zope.schema


class VideoAsset(zeit.cms.content.dav.DAVPropertiesAdapter):

    grokcore.component.implements(zeit.brightcove.interfaces.IVideoAsset)

    _video_id = zeit.cms.content.dav.DAVProperty(
        zope.schema.TextLine(),
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'video_id')

    _video_id_2 = zeit.cms.content.dav.DAVProperty(
        zope.schema.TextLine(),
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'video_id_2')

    zeit.cms.content.dav.mapProperties(
        zeit.brightcove.interfaces.IVideoAsset,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('audio_id',))

    @property
    def video(self):
        return zeit.cms.interfaces.ICMSContent(self._video_id, None)

    @video.setter
    def video(self, value):
        value = value and value.uniqueId
        self._video_id = value

    @property
    def video_2(self):
        return zeit.cms.interfaces.ICMSContent(self._video_id_2, None)

    @video_2.setter
    def video_2(self, value):
        value = value and value.uniqueId
        self._video_id_2 = value


class XMLReferenceUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):

    target_iface = zeit.brightcove.interfaces.IVideoAsset

    def update_with_context(self, node, av):
        while node.find('audio') is not None:
            node.remove(node.find('audio'))
        if av.audio_id:
            node.append(lxml.objectify.E.audio(audio_id=av.audio_id))

        while node.find('video') is not None:
            node.remove(node.find('video'))
        v1 = self.prefix_id(av.video)
        v2 = self.prefix_id(av.video_2)
        if v1 or v2:
            video = lxml.objectify.E.video()
            video.set('video_id', v1)
            video.set('video_id_2', v2)
            video.set('expires', self._expires(av.video, av.video_2))
            node.append(video)

    def prefix_id(self, content):
        if content is None:
            return ''
        return '%s%s' % (content.id_prefix, content.id)

    # XXX duplicated code from zeit.wysiwyg.html.VideoStep
    def _expires(self, video1, video2):
        all_expires = []
        maximum = datetime.datetime(datetime.MAXYEAR, 12, 31, tzinfo=pytz.UTC)
        for video in [video1, video2]:
            expires = getattr(video, 'expires', maximum)
            all_expires.append(expires)
        expires = min(all_expires)
        if expires == maximum:
            return ''
        return expires.isoformat()
