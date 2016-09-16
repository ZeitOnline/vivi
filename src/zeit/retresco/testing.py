import gocept.httpserverlayer.custom
import zeit.cms.content.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.testing
import zeit.content.article.testing
import zeit.content.image.testing
import zeit.workflow.testing


class RequestHandler(gocept.httpserverlayer.custom.RequestHandler):

    def do_GET(self):
        length = int(self.headers.get('content-length', 0))
        self.requests.append(dict(
            verb=self.command,
            path=self.path,
            body=self.rfile.read(length) if length else None,
        ))
        self.send_response(self.response_code)
        self.end_headers()
        self.wfile.write(self.response_body)

    do_POST = do_GET
    do_PUT = do_GET
    do_DELETE = do_GET


class HTTPLayer(gocept.httpserverlayer.custom.Layer):

    def testSetUp(self):
        super(HTTPLayer, self).testSetUp()
        self['request_handler'].requests = []
        self['request_handler'].response_body = '{}'
        self['request_handler'].response_code = 200

HTTP_LAYER = HTTPLayer(RequestHandler, name='HTTPLayer', module=__name__)


# XXX appending to product config is not very well supported right now
cms_product_config = zeit.cms.testing.cms_product_config.replace(
    '</product-config>', """\
  task-queue-search events
</product-config>""")


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
    'ftesting.zcml', product_config=cms_product_config +
    product_config +
    zeit.workflow.testing.product_config +
    zeit.content.article.testing.product_config +
    zeit.content.image.testing.product_config)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZCML_LAYER


class TagTestHelpers(object):
    """Helper to prefill DAV-Property used for keywords of a content object."""

    def set_tags(self, content, xml):
        """Prefill DAV-Property for keywords of `content` with `xml`.

        It inserts `xml` into a newly created DAV-property 'rankedTags' under
        the tagging-namespace key. `xml` is a string containing XML
        representing `Tag` objects, which requires `type` and `text`::

            <tag type="Person">Karen Duve</tag>
            <tag type="Location">Berlin</tag>

        """

        dav = zeit.connector.interfaces.IWebDAVProperties(content)
        name, ns = dav_key = (
            'rankedTags', 'http://namespaces.zeit.de/CMS/tagging')
        dav[dav_key] = """<ns:{tag} xmlns:ns="{ns}">
        <rankedTags>{0}</rankedTags></ns:{tag}>""".format(
            xml, ns=ns, tag=name)


def create_testcontent():
    content = zeit.cms.testcontenttype.testcontenttype.TestContentType()
    content.uniqueId = 'http://xml.zeit.de/testcontent'
    content.teaserText = 'teaser'
    content.title = 'title'
    zeit.cms.content.interfaces.IUUID(content).id = 'myid'
    return content
