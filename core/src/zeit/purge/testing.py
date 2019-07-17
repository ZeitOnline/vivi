from StringIO import StringIO
import gocept.httpserverlayer.custom
import socket
import time
import zeit.cms.testing
import zope.app.appsetup.product


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


class ProductConfigLayer(zeit.cms.testing.ProductConfigLayer):

    def setUp(self):
        config = product_config.format(
            port1=HTTP_LAYER1['http_port'], port2=HTTP_LAYER2['http_port'])
        self.config = zope.app.appsetup.product.loadConfiguration(
            StringIO(config))[self.package]
        super(ProductConfigLayer, self).setUp()

CONFIG_LAYER = ProductConfigLayer({}, bases=(
    zeit.cms.testing.CONFIG_LAYER, HTTP_LAYER1, HTTP_LAYER2))
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))
