import persistent

import zeit.cms.testing


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(zeit.cms.testing.CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class Content(persistent.Persistent):
    pass
