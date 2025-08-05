import persistent

import zeit.cms.testing
import zeit.connector.testing


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    features=['zeit.connector.sql'],
    bases=(zeit.cms.testing.CONFIG_LAYER, zeit.connector.testing.SQL_CONFIG_LAYER),
)
SQL_LAYER = zeit.connector.testing.SQLIsolationLayer(ZCML_LAYER)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(SQL_LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class Content(persistent.Persistent):
    pass
