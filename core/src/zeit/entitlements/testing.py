import zeit.cms.testing
import zeit.content.article.testing


class ArticleConfigLayer(zeit.cms.testing.ProductConfigLayer):
    def setUp(self):
        """
        Performance optimization, entitlements consider audioreferences
        which unfortunately require real articles
        """
        self.config = zeit.content.article.testing.CONFIG_LAYER.config
        super().setUp()


ARTICLE_CONFIG_LAYER = ArticleConfigLayer({}, package='zeit.content.article')


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    (zeit.cms.testing.CONFIG_LAYER, ARTICLE_CONFIG_LAYER), features=['zeit.connector.sql.zope']
)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER
