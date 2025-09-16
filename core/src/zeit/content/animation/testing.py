import zope.component

import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.article.testing
import zeit.content.image.testing


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    zeit.content.article.testing.CONFIG_LAYER, features=['zeit.connector.sql.zope']
)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)


class FixtureLayer(zeit.cms.testing.Layer):
    def setUp(self):
        self['gcs_storage'].stack_push()
        with self['rootFolder'](self['zodbDB-layer']) as root:
            with zeit.cms.testing.site(root):
                repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
                repository['article'] = zeit.content.article.testing.create_article()
                repository['image1'] = zeit.content.image.testing.create_image()
                repository['image2'] = zeit.content.image.testing.create_image()

    def tearDown(self):
        self['gcs_storage'].stack_pop()


LAYER = FixtureLayer(ZOPE_LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = LAYER
