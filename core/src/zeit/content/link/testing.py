import importlib.resources

import zeit.cms.testing
import zeit.push.testing


HERE = importlib.resources.files(__package__)
CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'source-blogs': f'file://{HERE}/blog_source.xml',
    },
    bases=zeit.push.testing.CONFIG_LAYER,
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(CONFIG_LAYER, features=['zeit.connector.sql.zope'])
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)
PUSH_LAYER = zeit.push.testing.FixtureLayer(ZOPE_LAYER)
LAYER = zeit.cms.testing.Layer(PUSH_LAYER)
WSGI_LAYER = zeit.cms.testing.WSGILayer(LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER
