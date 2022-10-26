from lxml.objectify import E
from urllib.parse import urlparse
from zeit.cms.content.interfaces import IUUID
from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.cms.i18n import MessageFactory as _
from zope.index.text.interfaces import ISearchableText
import grokcore.component as grok
import hashlib
import logging
import requests
import time
import zeit.cms.interfaces
import zeit.content.article.article
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zope.interface
import zope.security.management
import zope.security.proxy


log = logging.getLogger(__name__)


# QSTN: Better define this as dict (in ProductConfiguration) to replace
#       mapping in z.c.article.edit.browser.edit.VideoTagesschau.handle_update?
VIDEO_ATTRIBUTES = {
    'id', 'title', 'type', 'synopsis', 'video_url_hd',
    'video_url_hls_stream', 'video_url_hq', 'video_url_ln',
    'thumbnail_url_fullhd', 'thumbnail_url_large', 'thumbnail_url_small',
    'date_published', 'date_available'}


@grok.implementer(zeit.content.article.edit.interfaces.IVideoTagesschauAPI)
class VideoTagesschauAPI():

    def __init__(self, config):
        self.api_url_post = config['tagesschau-api-url-post']
        self.api_url_get = config['tagesschau-api-url-get']
        self.sig_uri = config['tagesschau-sig-uri']
        self.api_key = config['tagesschau-api-key']

    def request_videos(self, article):
        payload = self._prepare_payload(article)
        article_hash = hashlib.sha256(
            payload['article_text'].encode('utf-8')).hexdigest()

        # lookup for existing videos for given parameter
        video_recommendations = self._request_recommendations(
            article, payload, article_hash)
        if video_recommendations['recommendations']:
            log.info(f'Found tagesschauvideo for "{article.title}" '
                     f'{payload["article_custom_id"]}')
            return video_recommendations
        # NOTE: currently there is no way to do the following requests
        #       in one step to call video urls
        try:
            self._request(
                f'POST {self.api_url_post}?SIG_URI={self.sig_uri}'
                f'&API_KEY={self.api_key}&ART_HASH={article_hash}',
                json=payload)
        # TODO: more detailed exception report?
        except Exception as e:
            log.error(f'POST "{article.title}" '
                      f'[{payload["article_custom_id"]}] '
                      f'to Tagesschau: {e}')
        # NOTE: this sleep is just a guess; better: retry loop?
        time.sleep(3)
        return self._request_recommendations(
            article, payload, article_hash)

    def _request_recommendations(
            self, article, payload, article_hash):
        try:
            rget = self._request(
                f'GET {self.api_url_get}/{article_hash}')
            if rget.status_code == 200:
                return rget.json()
            if rget.status_code == 404:
                log.info(
                    f'404: No entry for current version of '
                    f'"{article.title}" '
                    f'{payload["article_custom_id"]}; '
                    f'key: {article_hash}')
            return {"recommendations": []}
        except Exception as e:
            log.error(f'GET Tagesschau video for "{article.title}" '
                      f'{payload["article_custom_id"]}: {e}',
                      exc_info=True)
            pass

    def _request(self, request, headers=None, **kw):
        verb, path = request.split(' ')
        method = getattr(requests, verb.lower())
        try:
            r = method(path, headers=headers, **kw)
            return r
        except Exception as e:
            log.error(f'ARD-API: {e}', exc_info=True)
            pass

    def _prepare_payload(self, article):
        uniqueId_parts = urlparse(article.uniqueId).path.split('/')
        filename = uniqueId_parts[-1]
        # new articles
        if filename.endswith('.tmp'):
            article_uri = f'{"/".join(uniqueId_parts[0:-1])}/'\
                f'{zeit.cms.interfaces.normalize_filename(article.title)}'
        else:
            article_uri = '/'.join(uniqueId_parts)
        body = ' '.join(ISearchableText(article).getSearchableText())
        payload = {
            'article_custom_id': IUUID(article).id,
            'article_title': article.title,
            'article_text': body,
            'article_uri': article_uri}
        return payload


@grok.implementer(zeit.content.article.edit.interfaces.IVideoTagesschau)
class VideoTagesschau(zeit.content.article.edit.block.Block):

    type = 'videotagesschau'

    _selected = ObjectPathAttributeProperty('.', 'selected')

    @property
    def tagesschauvideo(self):
        return self.tagesschauvideos.get(self._selected)

    @tagesschauvideo.setter
    def tagesschauvideo(self, selected):
        if selected is None:
            self._selected = None
        else:
            self._selected = selected.id

    @property
    def tagesschauvideos(self):
        result = {}
        for node in self.xml.iterchildren('video'):
            item = self._deserialize(node)
            result[item.id] = item
        return result

    @tagesschauvideos.setter
    def tagesschauvideos(self, videos):
        for node in self.xml.iterchildren('video'):
            self.xml.remove(node)
        for item in videos:
            self.xml.append(self._serialize(item))

    @staticmethod
    def _deserialize(node):
        nodes = dict()
        for attribute in VIDEO_ATTRIBUTES:
            nodes[attribute] = node.get(attribute)
        return Video(**nodes)

    @staticmethod
    def _serialize(video):
        nodes = dict()
        for attribute in VIDEO_ATTRIBUTES:
            nodes[attribute] = getattr(video, attribute)
        # NOTE: I was surprised that this works:
        return E.video(**nodes)


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = VideoTagesschau
    title = _('ARD Video')


class Video:

    def __init__(self, recommendations=None, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    def __eq__(self, other):
        if not zope.security.proxy.isinstance(other, type(self)):
            return False
        return self.id == other.id


@zope.interface.implementer(
    zeit.content.article.edit.interfaces.IVideoTagesschauAPI)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.content.article')
    return VideoTagesschauAPI(config)


@zope.interface.implementer(
    zeit.content.article.edit.interfaces.IVideoTagesschauAPI)
def MockVideoTagesschau():
    from unittest import mock  # testing dependency
    tagesschau_api = mock.Mock()
    zope.interface.alsoProvides(
        tagesschau_api,
        zeit.content.article.edit.interfaces.IVideoTagesschauAPI)
    return tagesschau_api
