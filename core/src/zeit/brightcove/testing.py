# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import BaseHTTPServer
import pkg_resources
import random
import simplejson
import threading
import urllib2
import urlparse
import zeit.brightcove.connection
import zeit.cms.testing
import zope.app.testing.functional



VIDEO_1234 = {
    'items': [
        {'creationDate': '1268018138802',
         'customFields': {
             'ressort': 'Auto',
             'newsletter': '1',
             'breaking-news': '0',
             'cmskeywords': 'Politik;koalition',
         },
         'economics': 'AD_SUPPORTED',
         'id': 70662056001L,
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
         'videoStillURL': 'http://videostillurl'}
    ],
    'page_number': 0,
    'page_size': 0,
    'total_count': -1,
}



class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    posts_received = []
    response = 200

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
            query.get('video_ids') == ['1234']):
            result = VIDEO_1234
        elif (query.get('command') == ['find_playlists_by_ids'] and
              query.get('playlist_ids') == ['2345']):
            result = VIDEO_1234
        else:
            result = {"items": [None],
                      "page_number": 0,
                      "page_size": 0,
                      "total_count": -1}
        self.send_response(self.response)
        self.end_headers()
        self.wfile.write(simplejson.dumps(result))

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


httpd_port = random.randint(30000, 40000)


product_config = """\
<product-config zeit.brightcove>
    read-token rdtkn
    write-token writetnk
    read-url http://localhost:%s/
    write-url http://localhost:%s/
</product-config>
""" % (httpd_port, httpd_port)


BrightcoveLayer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'BrightcoveLayer', allow_teardown=True,
    product_config=product_config)


class BrightcoveTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = BrightcoveLayer

    def setUp(self):
        super(BrightcoveTestCase, self).setUp()
        self.start_httpd()
        self.posts = RequestHandler.posts_received

    def tearDown(self):
        self.stop_httpd()
        self.posts[:] = []
        super(BrightcoveTestCase, self).tearDown()

    def start_httpd(self):
        self.httpd_running = True
        def run():
            server_address = ('localhost', httpd_port)
            httpd = BaseHTTPServer.HTTPServer(
                server_address, RequestHandler)
            while self.httpd_running:
                httpd.handle_request()
        t = threading.Thread(target=run)
        t.daemon = True
        t.start()

    def stop_httpd(self):
        self.httpd_running = False
        urllib2.urlopen('http://localhost:%s/die' % httpd_port)


# 70355221001
# 70740054001
# 70662056001
# 70355162001

