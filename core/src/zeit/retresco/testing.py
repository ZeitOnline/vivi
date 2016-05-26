import gocept.httpserverlayer.custom
import zeit.cms.testing


class RequestHandler(gocept.httpserverlayer.custom.RequestHandler):

    def do_GET(self):
        length = int(self.headers['content-length'])
        self.requests.append(dict(
            verb=self.command,
            path=self.path,
            body=self.rfile.read(length),
        ))
        self.send_response(self.response_code)
        self.end_headers()
        self.wfile.write(self.response_body)

    do_POST = do_GET
    do_PUT = do_GET


class HTTPLayer(gocept.httpserverlayer.custom.Layer):

    def testSetUp(self):
        super(HTTPLayer, self).testSetUp()
        self['request_handler'].requests = []
        self['request_handler'].response_body = '{}'
        self['request_handler'].response_code = 200

HTTP_LAYER = HTTPLayer(RequestHandler, name='HTTPLayer', module=__name__)


product_config = """
<product-config zeit.retresco>
    base-url http://localhost:[PORT]
</product-config>
"""


class ZCMLLayer(zeit.cms.testing.ZCMLLayer):

    defaultBases = (HTTP_LAYER,)

    def setUp(self):
        self.product_config = self.product_config.replace(
            '[PORT]', str(self['http_port']))
        super(ZCMLLayer, self).setUp()


ZCML_LAYER = ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config
    + product_config)
