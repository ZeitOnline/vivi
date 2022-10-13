import time
import requests
import zope.interface
import zope.security.management
import hashlib
from urllib.parse import urlparse
import zope.security.proxy
from lxml.objectify import E
from zeit.cms.content.property import ObjectPathAttributeProperty

import zeit.cms.interfaces
from zeit.cms.content.interfaces import IUUID
import zeit.content.article.article
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.cms.browser.view
from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import logging

log = logging.getLogger(__name__)

# QSTN: Better define this as dict (in ProductConfiguration) to replace
#       mapping in z.c.article.edit.browser.edit.VideoTagesschau.handle_update?
VIDEO_ATTRIBUTES = {'id', 'title', 'type', 'synopsis', 'video_url_hd',
    'video_url_hls_stream', 'video_url_hq', 'video_url_ln',
    'thumbnail_url_fullhd', 'thumbnail_url_large', 'thumbnail_url_small',
    'date_published', 'date_available'}


@grok.implementer(zeit.content.article.edit.interfaces.IVideoTagesschauAPI)
class VideoTagesschauAPI():

    def __init__(self, api_url_post, api_url_get, sig_uri, api_key):
        self.api_url_post = api_url_post
        self.api_url_get = api_url_get
        self.sig_uri = sig_uri
        self.api_key = api_key

    def request_videos(self, article):
        payload = self._prepare_payload(article)
        article_hash = hashlib.sha256(
            payload['article_text'].encode('utf-8')).hexdigest()
        headers = {'Access-Control-Allow-Headers': '*',
            'origin': 'https://www.zeit.de'}

        # lookup for existing videos for given parameter
        try:
            rget = requests.get(f'{self.api_url_get}/{article_hash}',
                                headers=headers)
            if rget.status_code == '200':
                log.info(f'Found tagesschauvideo for {article.title} '
                         f'[{payload["article_uuid"]}]')
                return rget.json()
        except Exception as e:
            log.error(f'GET Tagesschau video {article.title} '
                      f'[{payload["article_uuid"]}]: {e}')
            pass

        # NOTE: currently there is no way to do the following requests
        #       in one step to call video urls
        try:
            requests.post(f'{self.api_url_post}?SIG_URI={self.sig_uri}'
                f'&API_KEY={self.api_key}&ART_HASH={article_hash}',
                json=payload)
        # TODO: more detailed exception report?
        except Exception as e:
            log.error(f'POST {article.title} [{payload["article_uuid"]}] '
                      f'to Tagesschau: {e}')
        # NOTE: this sleep is just a guess; better: retry loop?
        time.sleep(3)
        try:
            rget = requests.get(f'{self.api_url_get}/{article_hash}',
                                headers=headers)
            return rget.json()
        except Exception as e:
            log.error(f'GET Tagesschau video {article.title} '
                      f'[{payload["article_uuid"]}]: {e}')

    def _prepare_payload(self, article):
        uniqueId_parts = urlparse(article.uniqueId).path.split('/')
        filename = uniqueId_parts[-1]
        # new articles
        if filename.endswith('.tmp'):
            article_uuid = f'{{urn:uuid:{filename.replace(".tmp", "")}}}'
            # TODO: Try to use filename if it exists
            article_uri = f'{"/".join(uniqueId_parts[0:-1])}/'\
                f'{zeit.cms.interfaces.normalize_filename(article.title)}'
        else:
            article_uuid = IUUID(article).id
            article_uri = "/".join(uniqueId_parts)
        payload = {'article_custom_id': article_uuid,
                'article_title': article.title,
                'article_text': self._xml2plain(article),
                'article_uri': article_uri}
        return payload

    def _xml2plain(self, article):
        # TODO: improve main_text? More than <p>?
        #       Does API like HTML with semantic tags?
        text_content = []
        for p in article.xml.body.xpath("//p//text()"):
            text = str(p).strip()
            if text:
                text_content.append(text)
        return ' '.join(text_content)


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
    title = _('Video ARD Tagesschau')


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
    return VideoTagesschauAPI(
        config['tagesschau-api-url-post'],
        config['tagesschau-api-url-get'],
        config['tagesschau-sig-uri'],
        config['tagesschau-api-key'])


@zope.interface.implementer(
    zeit.content.article.edit.interfaces.IVideoTagesschauAPI)
def MockVideoTagesschau():
    from unittest import mock  # testing dependency
    tagesschau_api = mock.Mock()
    zope.interface.alsoProvides(
        tagesschau_api,
        zeit.content.article.edit.interfaces.IVideoTagesschauAPI)
    return tagesschau_api
