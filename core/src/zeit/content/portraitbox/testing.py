import zeit.cms.testing
import zeit.content.image.testing
import zeit.content.portraitbox.interfaces


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    zeit.content.image.testing.CONFIG_LAYER, features=['zeit.connector.sql.zope']
)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)
WSGI_LAYER = zeit.cms.testing.WSGILayer(ZOPE_LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER
