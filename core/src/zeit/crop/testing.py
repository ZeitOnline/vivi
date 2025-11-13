# coding: utf8
import importlib.resources

import transaction

import zeit.cms.testing
import zeit.content.image.testing


HERE = importlib.resources.files(__package__)
CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'scale-source': f'file://{HERE}/scales.xml',
        'color-source': f'file://{HERE}/colors.xml',
    },
    bases=zeit.content.image.testing.CONFIG_LAYER,
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(CONFIG_LAYER, features=['zeit.connector.sql.zope'])
_zope_layer = zeit.cms.testing.RawZopeLayer(ZCML_LAYER)
ZOPE_LAYER = zeit.cms.testing.SQLIsolationSavepointLayer(_zope_layer)
WSGI_LAYER = zeit.cms.testing.WSGILayer(ZOPE_LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER


HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(
    zeit.cms.testing.WSGILayer(zeit.cms.testing.SQLIsolationTruncateLayer(_zope_layer))
)
WEBDRIVER_LAYER = zeit.cms.testing.WebdriverLayer(HTTP_LAYER)


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):
    layer = WEBDRIVER_LAYER
    window_width = 1100
    window_height = 600

    def setUp(self):
        super().setUp()
        zeit.content.image.testing.create_image_group()
        transaction.commit()
        self.open('/repository/group/@@imp.html')
