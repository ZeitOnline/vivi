# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import socket
import time
import zeit.cms.testing


class RequestHandler(zeit.cms.testing.BaseHTTPRequestHandler):

    response = 200
    need_time = 0

    def do_PURGE(self):
        print "Purging", self.__class__.__name__, self.path
        time.sleep(self.need_time)
        try:
            self.send_response(self.response)
            self.end_headers()
        except socket.error:
            pass


class Server1(RequestHandler):
    pass


class Server2(RequestHandler):
    pass


HTTPLayer1, port1 = zeit.cms.testing.HTTPServerLayer(Server1)
HTTPLayer2, port2 = zeit.cms.testing.HTTPServerLayer(Server2)

timeout = 1

product_config = """\
<product-config zeit.purge>
    servers localhost:%s localhost:%s
    public-prefix http://www.zeit.de/
    purge-timeout %s
</product-config>
""" % (port1, port2, timeout)


ZCMLLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=product_config)


class PurgeLayer(ZCMLLayer, HTTPLayer1, HTTPLayer2):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass
