import zeit.cms.testing
import zeit.content.image.testing
import zeit.content.portraitbox.interfaces


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(zeit.content.image.testing.CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER
