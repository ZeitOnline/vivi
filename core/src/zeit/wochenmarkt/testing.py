import importlib.resources

import zeit.cms.testing


HERE = importlib.resources.files(__package__)
CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'recipe-genres': 'rezept,rezept-vorstellung',
        'categories-url': f'file://{HERE}/tests/fixtures/categories.xml',
        'ingredients-url': f'file://{HERE}/tests/fixtures/ingredients.xml',
    },
    bases=zeit.cms.testing.CONFIG_LAYER,
)


class ArticleConfigLayer(zeit.cms.testing.ProductConfigLayer):
    def setUp(self):
        # Break circular dependency
        import zeit.content.article.testing

        self.config = zeit.content.article.testing.CONFIG_LAYER.config
        super().setUp()


ARTICLE_CONFIG_LAYER = ArticleConfigLayer({}, package='zeit.content.article')


class ModulesConfigLayer(zeit.cms.testing.ProductConfigLayer):
    def setUp(self):
        # Break circular dependency
        import zeit.content.modules.testing

        self.config = zeit.content.modules.testing.CONFIG_LAYER.config
        super().setUp()


MODULES_CONFIG_LAYER = ModulesConfigLayer({}, package='zeit.content.modules')


ZCML_LAYER = zeit.cms.testing.ZCMLLayer((CONFIG_LAYER, ARTICLE_CONFIG_LAYER, MODULES_CONFIG_LAYER))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER
