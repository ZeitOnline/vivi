# coding: utf8
import gocept.selenium
import importlib.resources
import zeit.cms.testing
import zeit.content.image.testing


product_config = """
<product-config zeit.crop>
    scale-source file://{here}/scales.xml
    color-source file://{here}/colors.xml
</product-config>
""".format(here=importlib.resources.files(__package__))


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    product_config, bases=(zeit.content.image.testing.CONFIG_LAYER,))
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):

    layer = WSGI_LAYER


HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = zeit.cms.testing.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):

    layer = WEBDRIVER_LAYER
    window_width = 1100
    window_height = 600

    def setUp(self):
        super().setUp()
        self.create_group()
        self.open_imp()

    def create_group(self):
        zeit.content.image.testing.create_image_group_with_master_image()

    def open_imp(self):
        self.open('/repository/group/@@imp.html')
