import gocept.httpserverlayer.wsgi
import gocept.selenium
import mock
import pkg_resources
import plone.testing
import zeit.cms.testing
import zope.component

product_config = """\
<product-config zeit.solr>
    solr-url http://internal.invalid
    public-solr-url http://public.invalid
    second-solr-url http://public.invalid
</product-config>

<product-config zeit.find>
    elasticsearch-url http://tms-backend.staging.zeit.de:80/elasticsearch
    elasticsearch-index foo_pool
</product-config>
"""


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    '../ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config)


class Layer(plone.testing.Layer):

    defaultBases = (ZCML_LAYER,)

    def setUp(self):
        import zeit.solr.interfaces
        self.solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)

    def testSetUp(self):
        self.solr._send_request = mock.Mock()

    def testTearDown(self):
        del self.solr._send_request

    def set_result(self, package, filename):
        self.solr._send_request.return_value = pkg_resources.resource_string(
            package, filename)


LAYER = Layer()

WSGI_LAYER = zeit.cms.testing.WSGILayer(name='WSGILayer', bases=(LAYER,))
HTTP_LAYER = gocept.httpserverlayer.wsgi.Layer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = gocept.selenium.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
SELENIUM_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))
