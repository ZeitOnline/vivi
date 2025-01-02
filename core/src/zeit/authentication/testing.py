import zeit.cms.testing
import zeit.cms.zope


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'authenticator-plugins': 'principalregistry',
        'credentials-plugins': 'xmlrpc-basic-auth',
        'ad-tenant': 'common',
        'ad-client-id': 'none',
        'ad-client-secret': 'none',
        'ad-timeout': '1',
    },
    bases=(zeit.cms.testing.CONFIG_LAYER,),
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER
