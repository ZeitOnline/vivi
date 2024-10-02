import importlib.resources

import zeit.cms.testing
import zeit.wochenmarkt.categories
import zeit.wochenmarkt.ingredients


HERE = importlib.resources.files(__package__)
CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'categories-url': f'file://{HERE}/tests/fixtures/categories.xml',
        'ingredients-url': f'file://{HERE}/tests/fixtures/ingredients.xml',
    },
    bases=(zeit.cms.testing.CONFIG_LAYER,),
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting.zcml', bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class RecipeCategoriesHelper:
    """Mixin for tests which need some recipe category infrastrucutre."""

    def get_category(self, code):
        category = zeit.wochenmarkt.categories.RecipeCategory(code=code, name='_' + code)
        return category

    def setup_categories(self, *codes):
        categories = {}
        for code in codes:
            categories[code] = self.get_category(code)
        return categories
