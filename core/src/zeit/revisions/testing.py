from unittest import mock

import lxml

from zeit.connector.testing import GCS_SERVER_LAYER
import zeit.cms.checkout
import zeit.cms.testing
import zeit.content.article.testing


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'storage-project': 'ignored_by_emulator',
        'storage-bucket': GCS_SERVER_LAYER.bucket,
    },
    bases=(zeit.content.article.testing.CONFIG_LAYER,),
)


ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting.zcml', bases=(CONFIG_LAYER, GCS_SERVER_LAYER))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER

    @property
    def config(self):
        return """<revisions>
          <filter/>
        </revisions>
        """

    def setUp(self):
        super().setUp()
        self.patch = mock.patch(
            'zeit.revisions.revisions.FilterSource._get_tree',
            side_effect=lambda: lxml.etree.fromstring(self.config),
        )
        self.patch.start()
        source = zeit.revisions.revisions.FILTERS.factory
        # XXX Have to pass the instance because of zc.factory init shenanigans.
        source._values.invalidate(source)

    def tearDown(self):
        self.patch.stop()
        super().tearDown()
