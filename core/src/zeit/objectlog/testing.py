import persistent

import zeit.cms.testing
import zeit.connector.testing


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(zeit.cms.testing.CONFIG_LAYER)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)

SQL_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    features=['zeit.connector.sql'],
    bases=(zeit.cms.testing.CONFIG_LAYER, zeit.connector.testing.SQL_CONFIG_LAYER),
)
SQL_ZOPE_LAYER = zeit.cms.testing.ZopeLayer(SQL_ZCML_LAYER)
SQL_CONNECTOR_LAYER = zeit.connector.testing.SQLDatabaseLayer(SQL_ZOPE_LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class SQLTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = SQL_CONNECTOR_LAYER


class Content(persistent.Persistent):
    pass
