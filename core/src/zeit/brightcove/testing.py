# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import json
import mock
import pkg_resources
import time
import transaction
import urlparse
import zeit.brightcove.converter
import zeit.cms.interfaces
import zeit.cms.testing
import zeit.solr.testing
import zeit.workflow.testing
import zope.component


VIDEO_1234 = {
    'creationDate': '1268018138802',
    'customFields': {
        'ressort': 'Auto',
        'newsletter': '1',
        'breaking-news': '0',
        'cmskeywords': 'Politik;koalition',
        'banner': '1',
        'banner-id': '99887',
    },
    'economics': 'AD_SUPPORTED',
    'id': 1234,
    'lastModifiedDate': '1268053197824',
    'length': 152640,
    'linkText': None,
    'linkURL': None,
    'longDescription': u'Mehr Glanz, Glamour und erwartungsvolle Spannung',
    'name': 'Starrummel auf dem Roten Teppich zur 82. Oscar-Verleihung',
    'playsTotal': None,
    'playsTrailingWeek': None,
    'publishedDate': '1268053197823',
    'referenceId': '2010-03-08T023523Z_1_OVE6276PP_RTRMADC_0_ONLINE',
    'shortDescription': u'Glanz, Glamour und erwartungsvolle Spannung',
    'tags': ['Vermischtes'],
    'thumbnailURL': 'http://thumbnailurl',
    'videoStillURL': 'http://videostillurl',
    'itemState': 'ACTIVE',
    'endDate': '1269579600000',
    'FLVURL': 'http://flvurl',
}

VIDEO_6789 = {
    'creationDate': '1268018138802',
    'customFields': {
        'ressort': 'Auto',
        'newsletter': '1',
        'breaking-news': '0',
        'cmskeywords': 'Politik;koalition',
    },
    'economics': 'AD_SUPPORTED',
    'id': 6789,
    'lastModifiedDate': '1268053197824',
    'length': 152640,
    'linkText': None,
    'linkURL': None,
    'longDescription': u'Once more, a video. Wirh a very long description',
    'name': 'Woah, a video',
    'playsTotal': None,
    'playsTrailingWeek': None,
    'publishedDate': '1268053197823',
    'referenceId': '2010-03-08T023523Z_1_OVE6276PP_RTRMADC_0_ONLINE',
    'shortDescription': u'rockon, video',
    'tags': ['Vermischtes'],
    'thumbnailURL': 'http://thumbnailurl',
    'videoStillURL': 'http://videostillurl',
    'itemState': 'ACTIVE',
    'endDate': '',
}

PLAYLIST_2345 = {
    'filterTags': ['Film'],
    'id': 2345,
    'name': 'Videos zum Thema Film',
    'shortDescription': 'Videos in kurz',
    'thumbnailURL': None,
    'videoIds': [1234, 6789],
}


# Define responses. Note that the API returns total_count == -1 when there is
# only one page. *puke*

SINGLE_VIDEO_RESPONSE = {
    'items': [VIDEO_1234],
    'page_number': 0,
    'page_size': 0,
    'total_count': -1,
}

ANOTHER_SINGLE_VIDEO_RESPONSE = {
    'items': [VIDEO_6789],
    'page_number': 0,
    'page_size': 0,
    'total_count': -1,
}

SINGLE_PLAYLIST_RESPONSE = {
    'items': [PLAYLIST_2345],
    'page_number': 0,
    'page_size': 0,
    'total_count': -1,
}
SINGLE_PLAYLIST_RESPONSE['items'][0]['id'] = 2345


VIDEO_LIST_RESPONSE = {
    'items': [VIDEO_1234, VIDEO_1234.copy(), VIDEO_6789],
    'page_number': 0,
    'page_size': 0,
    'total_count': -1,
}
VIDEO_LIST_RESPONSE['items'][1]['id'] = 9876


PLAYLIST_LIST_RESPONSE = {
    'items': [PLAYLIST_2345, PLAYLIST_2345.copy()],
    'page_number': 0,
    'page_size': 0,
    'total_count': -1,
}
PLAYLIST_LIST_RESPONSE['items'][1]['id'] = 3456


class RequestHandler(zeit.cms.testing.BaseHTTPRequestHandler):

    posts_received = []
    response = 200
    sleep = 0

    def do_GET(self):
        if self.path == '/die':
            self.send_response(200)
            self.end_headers()
            return
        if not self.path.startswith('/?'):
            self.send_response(500)
            self.end_headers()
            return
        query = urlparse.parse_qs(self.path[2:])
        if (query.get('command') == ['find_videos_by_ids'] and
            query.get('video_ids') == ['1234'] and
            query.get('video_fields')):
            result = SINGLE_VIDEO_RESPONSE
        elif (query.get('command') == ['find_videos_by_ids'] and
            query.get('video_ids') == ['6789'] and
            query.get('video_fields')):
            result = ANOTHER_SINGLE_VIDEO_RESPONSE
        elif (query.get('command') == ['find_playlists_by_ids'] and
              query.get('playlist_ids') == ['2345']):
            result = SINGLE_PLAYLIST_RESPONSE
        elif (query.get('command') == ['find_modified_videos'] and
              query.get('video_fields')):
            result = VIDEO_LIST_RESPONSE
        elif (query.get('command') == ['find_all_playlists']):
            result = PLAYLIST_LIST_RESPONSE
        else:
            result = {"items": [None],
                      "page_number": 0,
                      "page_size": 0,
                      "total_count": -1}
        time.sleep(self.sleep)
        self.send_response(self.response)
        self.end_headers()
        self.wfile.write(json.dumps(result))

    def do_POST(self):
        length = int(self.headers['content-length'])
        self.posts_received.append(dict(
            path=self.path,
            data=self.rfile.read(length),
        ))
        self.send_response(self.response)
        self.end_headers()
        self.wfile.write('{"result":{}}')

    def log_message(self, format, *args):
        pass


BrightcoveHTTPLayer, httpd_port = zeit.cms.testing.HTTPServerLayer(
    RequestHandler)


product_config = """\
<product-config zeit.brightcove>
    read-token rdtkn
    write-token writetnk
    read-url http://localhost:%s/
    write-url http://localhost:%s/
    source-serie file://%s
    timeout 300
    video-folder video
    playlist-folder video/playlist
</product-config>
""" % (httpd_port,
       httpd_port,
       pkg_resources.resource_filename(__name__, 'tests/serie.xml'))


BrightcoveZCMLLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=(
        zeit.cms.testing.cms_product_config +
        zeit.solr.testing.product_config +
        zeit.workflow.testing.product_config +
        product_config))


def update_repository(root):
    with zeit.cms.testing.site(root):
        with transaction:
            zeit.brightcove.update.update_from_brightcove()


class BrightcoveLayer(BrightcoveHTTPLayer,
                      BrightcoveZCMLLayer,
                      zeit.solr.testing.SolrMockLayerBase):

    @classmethod
    def setUp(cls):
        product_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        product_config['publish-script'] = 'true'
        product_config['retract-script'] = 'true'

        cls.resolve_patch = mock.patch(
            'zeit.brightcove.converter.resolve_video_id',
            new=cls.resolve_video_id)
        cls.resolve_patch.start()

    @staticmethod
    def resolve_video_id(video_id):
        return zeit.brightcove.converter.Video.find_by_id(video_id).uniqueId

    @classmethod
    def tearDown(cls):
        cls.resolve_patch.stop()

    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def testTearDown(cls):
        RequestHandler.posts_received[:] = []


class BrightcoveTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = BrightcoveLayer

    def setUp(self):
        super(BrightcoveTestCase, self).setUp()
        self.posts = RequestHandler.posts_received
        update_repository(self.getRootFolder())
        transaction.commit()
        zeit.workflow.testing.run_publish()
        # clear changes made by the checkout/checkin-cycle during publishing
        RequestHandler.posts_received[:] = []


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('layer', BrightcoveLayer)
    kw['package'] = zope.testing.doctest._normalize_module(kw.get('package'))
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)



# test video IDs from the live system.
# 70355221001
# 70740054001
# 70662056001
# 70355162001
