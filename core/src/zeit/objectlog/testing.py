import persistent

import zeit.cms.testing


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    features=['zeit.connector.sql'],
    bases=(zeit.cms.testing.CONFIG_LAYER, zeit.cms.testing.SQL_LAYER),
)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class Content(persistent.Persistent):
    pass
