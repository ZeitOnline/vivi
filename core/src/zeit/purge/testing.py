import gocept.httpserverlayer.custom
import socket
import time
import zeit.cms.testing


class RequestHandler(gocept.httpserverlayer.custom.RequestHandler):

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


HTTP_LAYER1 = gocept.httpserverlayer.custom.Layer(
    Server1, name='PurgeHTTPLayer1', module=__name__)
HTTP_LAYER2 = gocept.httpserverlayer.custom.Layer(
    Server2, name='PurgeHTTPLayer2', module=__name__)

timeout = 1

product_config = """\
<product-config zeit.purge>
    servers localhost:{port1} localhost:{port2}
    public-prefix http://www.zeit.de/
    purge-timeout %s
</product-config>
""" % timeout


class ZCMLLayer(zeit.cms.testing.ZCMLLayer):

    defaultBases = (HTTP_LAYER1, HTTP_LAYER2)

    def setUp(self):
        self.product_config = self.product_config.format(
            port1=HTTP_LAYER1['http_port'], port2=HTTP_LAYER2['http_port'])
        super(ZCMLLayer, self).setUp()

ZCML_LAYER = ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config)
