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
VIDEO_ATTRIBUTES= {'id', 'title', 'type', 'synopsis', 'video_url_hd',
    'video_url_hls_stream', 'video_url_hq', 'video_url_ln',
    'thumbnail_url_fullhd', 'thumbnail_url_large', 'thumbnail_url_small',
    'date_published', 'date_available'}

DUMMY_RESPONSE = '''
{"cutoff": 1.975,
 "recommendations": [{"main_title": "NEU TITEL 1 Ukraine meldet russische Angriffe auf Infrastruktur und Erfolge bei Rückeroberungen, die Diskussion um Waffenlieferungen dauert an",
                      "program_id": "crid://daserste.de/tagesschau24/7dd07892-7528-43f8-9a52-76679ebfc65dAAAXXX/1",
                      "published_start_time": "2022-09-12T11:02:00",
                      "score": 101.98643,
                      "search_strategy": "hotnews-no-local",
                      "short_synopsis": "TITEL 1 Ukraine meldet russische Angriffe auf Infrastruktur und Erfolge bei Rückeroberungen, die Diskussion um Waffenlieferungen dauert an",
                      "start_of_availability": "2022-09-12T11:02:59",
                      "thumbnail_uris": {"fullhd": "https://www.tagesschau.de/multimedia/bilder/sendungsbild-1010231AAAXXX~_v-videowebl.jpg",
                                         "large": "https://www.tagesschau.de/multimedia/bilder/sendungsbild-1010231XXX~_v-videowebm.jpg",
                                         "small": "https://www.tagesschau.de/multimedia/bilder/sendungsbild-1010231XXX~_v-videowebs.jpg"},
                      "video_uris": {"hd": "https://media.tagesschau.de/video/2022/0912/TV-20220912-1057-5500.webxl.h264.mp4",
                                     "hlsStream": "https://adaptive.tagesschau.de/i/video/2022/0912/TV-20220912-1057-5500.,webl.h264,webs.h264,webm.h264,webxl.h264,webxxl.h264,.mp4.csmil/master.m3u8",
                                     "hq": "https://media.tagesschau.de/video/2022/0912/TV-20220912-1057-5500.webl.h264.mp4",
                                     "ln": "https://media.tagesschau.de/video/2022/0912/TV-20220912-1057-5500.webs.h264.mp4"}},
                     {"main_title": "TITEL 2 Ukraine meldet russische Angriffe auf Infrastruktur und Erfolge bei Rückeroberungen, die Diskussion um Waffenlieferungen dauert an",
                      "program_id": "crid://daserste.de/tagesschau24/7dd07892-7528-43f8-9a52-76679ebfc65dYYY/1",
                      "published_start_time": "2022-09-12T11:02:00",
                      "score": 101.98643,
                      "search_strategy": "hotnews-no-local",
                      "short_synopsis": "TITEL 2 Ukraine meldet russische Angriffe auf Infrastruktur und Erfolge bei Rückeroberungen, die Diskussion um Waffenlieferungen dauert an",
                      "start_of_availability": "2022-09-12T11:02:59",
                      "thumbnail_uris": {"fullhd": "https://www.tagesschau.de/multimedia/bilder/sendungsbild-1010231YYY~_v-videowebl.jpg",
                                         "large": "https://www.tagesschau.de/multimedia/bilder/sendungsbild-1010231YYY~_v-videowebm.jpg",
                                         "small": "https://www.tagesschau.de/multimedia/bilder/sendungsbild-1010231YYY~_v-videowebs.jpg"},
                      "video_uris": {"hd": "https://media.tagesschau.de/video/2022/0912/TV-20220912-1057-5500.webxl.h264.mp4",
                                     "hlsStream": "https://adaptive.tagesschau.de/i/video/2022/0912/TV-20220912-1057-5500.,webl.h264,webs.h264,webm.h264,webxl.h264,webxxl.h264,.mp4.csmil/master.m3u8",
                                     "hq": "https://media.tagesschau.de/video/2022/0912/TV-20220912-1057-5500.webl.h264.mp4",
                                     "ln": "https://media.tagesschau.de/video/2022/0912/TV-20220912-1057-5500.webs.h264.mp4"}},
                     {"main_title": "TITEL 3 Ukraine meldet russische Angriffe auf Infrastruktur und Erfolge bei Rückeroberungen, die Diskussion um Waffenlieferungen dauert an",
                      "program_id": "crid://daserste.de/tagesschau24/7dd07892-7528-43f8-9a52-76679ebfc65dZZZ/1",
                      "published_start_time": "2022-09-12T11:02:00",
                      "score": 101.98643,
                      "search_strategy": "hotnews-no-local",
                      "short_synopsis": "TITEL 2 Ukraine meldet russische Angriffe auf Infrastruktur und Erfolge bei Rückeroberungen, die Diskussion um Waffenlieferungen dauert an",
                      "start_of_availability": "2022-09-12T11:02:59",
                      "thumbnail_uris": {"fullhd": "https://www.tagesschau.de/multimedia/bilder/sendungsbild-1010231ZZZ~_v-videowebl.jpg",
                                         "large": "https://www.tagesschau.de/multimedia/bilder/sendungsbild-1010231ZZZ~_v-videowebm.jpg",
                                         "small": "https://www.tagesschau.de/multimedia/bilder/sendungsbild-1010231ZZZ~_v-videowebs.jpg"},
                      "video_uris": {"hd": "https://media.tagesschau.de/video/2022/0912/TV-20220912-1057-5500.webxl.h264.mp4",
                                     "hlsStream": "https://adaptive.tagesschau.de/i/video/2022/0912/TV-20220912-1057-5500.,webl.h264,webs.h264,webm.h264,webxl.h264,webxxl.h264,.mp4.csmil/master.m3u8",
                                     "hq": "https://media.tagesschau.de/video/2022/0912/TV-20220912-1057-5500.webl.h264.mp4",
                                     "ln": "https://media.tagesschau.de/video/2022/0912/TV-20220912-1057-5500.webs.h264.mp4"}}],
 "src_txt_hash": "881424269bcdd572e37c6ef3ff702baefb7845e9a12a22518e062e0b5f194e9a"}
'''

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
        except Exception:
            log.error(f'GET Tagesschau video {article.title} '
                      f'[{payload["article_uuid"]}]: {e}')
            pass

        # NOTE: currently there is no way to do the following requests
        #       in one step to call video urls
        try:
            rpost = requests.post(f'{self.api_url_post}?SIG_URI={self.sig_uri}'
                f'&API_KEY={self.api_key}&ART_HASH={article_hash}', json=payload)
        # TODO: more detailed exception report?
        except Exception as e:
            log.error(f'POST {article.title} [{payload["article_uuid"]}] '
                      f'to Tagesschau: {e}')
            # TODO return something?
        # NOTE: this sleep is just a guess
        # better: retry loop?
        time.sleep(3)
        try:
            rget = requests.get(f'{self.api_url_get}/{article_hash}',
                                headers=headers)
            # TODO
            ### self.errors = (zeit.content.article.edit.interfaces.TagesschauError(),)
            ### self.status = _('There were errors')
            ### self.send_message('Hallo', type='error')
            import pdb; pdb.set_trace()
            # DUMMY:
            # import json
            # return json.loads(DUMMY_RESPONSE)
            return rget.json()
        except Exception as e:
            log.error(f'GET Tagesschau video {article.title} '
                      f'[{payload["article_uuid"]}]: {e}')

    def _prepare_payload(self, article):
        uniqueId_parts = urlparse(article.uniqueId).path.split('/')
        filename = uniqueId_parts[-1]
        # for new articles
        if filename.endswith('.tmp'):
            article_uuid = f'{{urn:uuid:{filename.replace(".tmp", "")}}}'
            # TODO: Try to use real URI
            article_uri = f'{"/".join(uniqueId_parts[0:-1])}/'\
                f'{zeit.cms.interfaces.normalize_filename(article.title)}'
        else:
            # TODO
            article_uuid = 'du-123-mmy-456'
            article_uri = 'http://www.dumm.y'
        payload = {'article_custom_id': article_uuid,
                'article_title': article.title,
                'article_text': self._xml2plain(article),
                'article_uri': article_uri}
        return payload

    def _xml2plain(self, article):
        text_content = []
        # TODO: improve main_text? More than <p>?
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
