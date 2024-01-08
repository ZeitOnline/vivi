import importlib.resources

import zeit.cmp.testing
import zeit.cms.testing


CONFIG_LAYER = zeit.cmp.testing.CONFIG_LAYER
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))

schema_url = 'file://{here}/testdata/openapi.yaml'.format(
    here=importlib.resources.files(__package__)
)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER
