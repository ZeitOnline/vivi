# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import lxml.objectify
import zeit.brightcove.interfaces
import zeit.cms.content.dav
import zeit.cms.interfaces
import zope.schema


class VideoAsset(zeit.cms.content.dav.DAVPropertiesAdapter):

    grokcore.component.implements(zeit.brightcove.interfaces.IVideoAsset)

    _video_id = zeit.cms.content.dav.DAVProperty(
        zope.schema.Int(),
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'video_id')

    _video_id_2 = zeit.cms.content.dav.DAVProperty(
        zope.schema.Int(),
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'video_id_2')

    zeit.cms.content.dav.mapProperties(
        zeit.brightcove.interfaces.IVideoAsset,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('audio_id',))

    @property
    def video(self):
        return zeit.cms.interfaces.ICMSContent(
            self._get_unique_id(self._video_id), None)

    @video.setter
    def video(self, value):
        value = value.id if value else None
        self._video_id = value

    @property
    def video_2(self):
        return zeit.cms.interfaces.ICMSContent(
            self._get_unique_id(self._video_id_2), None)

    @video_2.setter
    def video_2(self, value):
        value = value.id if value else None
        self._video_id_2 = value

    def _get_unique_id(self, id_):
        return 'http://video.zeit.de/video/%s' % (id_,)


class XMLReferenceUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):

    target_iface = zeit.brightcove.interfaces.IVideoAsset

    def update_with_context(self, node, av):
        while node.find('audio') is not None:
            node.remove(node.find('audio'))
        if av.audio_id:
            node.append(lxml.objectify.E.audio(audio_id=av.audio_id))

        while node.find('video') is not None:
            node.remove(node.find('video'))
        v1 = str(av.video.id) if av.video else ''
        v2 = str(av.video_2.id) if av.video_2 else ''
        if v1 or v2:
            video = lxml.objectify.E.video()
            video.set('video_id', v1)
            video.set('video_id_2', v2)
            node.append(video)
