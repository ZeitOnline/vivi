import datetime
import grokcore.component
import lxml.objectify
import pytz
import zeit.content.video.interfaces
import zeit.cms.content.dav
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zope.schema


def get_expires(*videos):
    """returns the earliest expire date of the two objects."""

    # an expires value might
    # - not exist on the object (if it's a Playlist)
    # - exist but be None (if a Video doesn't expire)
    all_expires = []
    maximum = datetime.datetime(datetime.MAXYEAR, 12, 31, tzinfo=pytz.UTC)
    for video in videos:
        if video is None:
            continue
        expires = getattr(video, 'expires', None)
        if expires is None:
            expires = maximum
        all_expires.append(expires)
    if all_expires:
        expires = min(all_expires)
    if not all_expires or expires == maximum:
        return ''
    return expires.isoformat()


class VideoAsset(zeit.cms.content.dav.DAVPropertiesAdapter):

    grokcore.component.implements(zeit.content.video.interfaces.IVideoAsset)

    _video_id = zeit.cms.content.dav.DAVProperty(
        zope.schema.TextLine(),
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'video_id')

    _video_id_2 = zeit.cms.content.dav.DAVProperty(
        zope.schema.TextLine(),
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'video_id_2')

    zeit.cms.content.dav.mapProperties(
        zeit.content.video.interfaces.IVideoAsset,
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

    target_iface = zeit.content.video.interfaces.IVideoAsset

    def update_with_context(self, node, av):
        while node.find('audio') is not None:
            node.remove(node.find('audio'))
        if av.audio_id:
            node.append(lxml.objectify.E.audio(audio_id=av.audio_id))

        while node.find('video') is not None:
            node.remove(node.find('video'))
        v1 = self.prefix_id(av.video)
        v2 = self.prefix_id(av.video_2)
        href = av.video and av.video.uniqueId or ''
        href2 = av.video_2 and av.video_2.uniqueId or ''
        if v1 or v2:
            video = lxml.objectify.E.video()
            video.set('href', href)
            video.set('href2', href2)
            video.set('expires', get_expires(av.video, av.video_2))
            # old style ID
            video.set('video_id', v1)
            video.set('video_id_2', v2)
            node.append(video)

    def prefix_id(self, content):
        if content is None:
            return ''
        return '%s%s' % (content.id_prefix, content.__name__)
