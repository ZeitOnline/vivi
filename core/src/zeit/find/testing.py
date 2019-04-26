import gocept.httpserverlayer.wsgi
import gocept.selenium
import json
import mock
import pkg_resources
import plone.testing
import zeit.cms.testing
import zeit.find.interfaces
import zope.component

product_config = """\
<product-config zeit.find>
    elasticsearch-url http://tms-backend.staging.zeit.de:80/elasticsearch
    elasticsearch-index foo_pool
</product-config>
"""


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config)


class Layer(plone.testing.Layer):

    defaultBases = (ZCML_LAYER,)

    def setUp(self):
        self.search = zope.component.getUtility(
            zeit.find.interfaces.ICMSSearch)

    def testSetUp(self):
        self.search.client.search = mock.Mock()

    def testTearDown(self):
        del self.search.client.search

    def set_result(self, package, filename):
        value = pkg_resources.resource_string(package, filename)
        self.search.client.search.return_value = json.loads(value)


LAYER = Layer()

WSGI_LAYER = zeit.cms.testing.WSGILayer(name='WSGILayer', bases=(LAYER,))
HTTP_LAYER = gocept.httpserverlayer.wsgi.Layer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = gocept.selenium.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
SELENIUM_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))
