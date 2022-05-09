import grokcore.component as grok
import logging
import zeit.brightcove.convert
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.connector.search
import zope.component


log = logging.getLogger(__name__)


# Defined in zeit.content.video.video.Video.external_id
BRIGHTCOVE_ID = zeit.connector.search.SearchVar(
    'id', 'http://namespaces.zeit.de/CMS/brightcove')


def resolve_video_id(video_id):
    connector = zope.component.getUtility(
        zeit.connector.interfaces.IConnector)
    result = list(
        connector.search([BRIGHTCOVE_ID], BRIGHTCOVE_ID == video_id))
    if not result:
        raise LookupError(video_id)
    if len(result) > 1:
        msg = 'Found multiple CMS objects with video id %r.' % video_id
        log.warning(msg)
        raise LookupError(msg)
    result = result[0]
    unique_id = result[0]
    return unique_id


def query_video_id(video_id, default=None):
    """Resolve video or return a default value."""
    try:
        return resolve_video_id(video_id)
    except LookupError:
        return default


@grok.adapter(str, name='http://video.zeit.de/')
@grok.implementer(zeit.cms.interfaces.ICMSContent)
def adapt_old_video_id_to_new_object(old_id):
    video_prefix = 'http://video.zeit.de/video/'
    playlist_prefix = 'http://video.zeit.de/playlist/'
    if old_id.startswith(video_prefix):
        video_id = old_id.replace(video_prefix, '', 1)
        return zeit.cms.interfaces.ICMSContent(query_video_id(video_id), None)
    elif old_id.startswith(playlist_prefix):
        pls_id = old_id.replace(playlist_prefix, '', 1)
        return zeit.brightcove.convert.playlist_location(None).get(pls_id)
