import gocept.selenium
import json
import mock
import pkg_resources
import plone.testing
import zeit.cms.testing
import zeit.content.image.testing
import zeit.find.interfaces
import zope.component

product_config = """\
<product-config zeit.find>
    elasticsearch-url http://tms-backend.staging.zeit.de:80/elasticsearch
    elasticsearch-index foo_pool
</product-config>
"""


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(product_config, bases=(
    zeit.content.image.testing.CONFIG_LAYER,))
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))


class Layer(plone.testing.Layer):

    defaultBases = (ZOPE_LAYER,)

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
HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = zeit.cms.testing.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
SELENIUM_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))
